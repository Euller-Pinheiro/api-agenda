# api-agenda

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-C9A84C)
![CI](https://github.com/Euller-Pinheiro/api-agenda/actions/workflows/ci.yml/badge.svg)
![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

**[English below](#english)**

API REST de **agendamento de serviços** — profissionais, serviços, clientes e horários — construída com **FastAPI, SQLAlchemy e PostgreSQL**.

## Por que este projeto

Agenda parece simples até aparecerem os casos reais: dois atendimentos que se sobrepõem por um minuto, o profissional que muda a disponibilidade, o fuso horário, o lembrete que precisa sair mesmo se o servidor reiniciar. O coração deste projeto é a regra de conflito de horários, coberta por testes contra um banco PostgreSQL de verdade.

## O que está a caminho

O projeto está sendo construído em entregas pequenas, cada uma com testes e CI. Acompanhe pelos commits e pull requests.

- [x] Estrutura do projeto e cadastros de profissionais, serviços e clientes
- [ ] Disponibilidade semanal e detecção de conflito de horários
- [ ] Autenticação com JWT e perfis de acesso
- [ ] Lembretes por e-mail em fila
- [ ] Paginação, filtros e erros padronizados

## Como rodar

Pré-requisito: Docker com o plugin Compose.

```bash
docker compose up --build
```

A API sobe em <http://localhost:8000>, aplica as migrações sozinha e publica a documentação interativa em <http://localhost:8000/docs> (Swagger) e <http://localhost:8000/redoc>.

### Desenvolvimento local e testes

```bash
docker compose up -d banco          # só o PostgreSQL (cria também o banco agenda_test)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn agenda.principal:app --reload

pytest                               # testes contra o PostgreSQL de verdade
ruff check . && ruff format --check . && mypy
```

Os testes usam `DATABASE_URL` (padrão: `postgresql+psycopg://agenda:agenda@localhost:5432/agenda_test`).

## Endpoints desta etapa

| Método | Caminho | O que faz |
|---|---|---|
| `GET` | `/saude` | Verifica se a API está no ar |
| `GET` `POST` | `/servicos` | Lista (filtro `?ativo=`) e cria serviços |
| `GET` `PATCH` `DELETE` | `/servicos/{id}` | Detalha, altera e remove |
| `GET` | `/servicos/{id}/profissionais` | Quem atende o serviço (filtro `?ativo=`) |
| `GET` `POST` | `/profissionais` | Lista (filtro `?ativo=`) e cria profissionais |
| `GET` `PATCH` `DELETE` | `/profissionais/{id}` | Detalha, altera e remove |
| `GET` `PUT` | `/profissionais/{id}/servicos` | Serviços que o profissional atende (o `PUT` substitui a lista) |
| `GET` `POST` | `/clientes` | Lista (busca `?busca=` por nome ou e-mail) e cria clientes |
| `GET` `PATCH` `DELETE` | `/clientes/{id}` | Detalha, altera e remove |

Exemplo:

```bash
curl -X POST localhost:8000/servicos -H 'content-type: application/json' \
  -d '{"nome": "Corte de cabelo", "duracao_minutos": 30, "preco_centavos": 4990}'
```

```json
{"id": 1, "nome": "Corte de cabelo", "descricao": null, "duracao_minutos": 30,
 "preco_centavos": 4990, "ativo": true, "criado_em": "...", "atualizado_em": "..."}
```

### Códigos de resposta

| Código | Quando |
|---|---|
| `201` | Recurso criado |
| `204` | Recurso removido |
| `404` | Id inexistente — `{"detail": "Serviço 42 não encontrado."}` |
| `409` | Nome de serviço ou e-mail já cadastrado |
| `422` | Corpo inválido: campo faltando, valor fora da faixa, campo desconhecido, `null` em campo obrigatório, serviço inexistente no vínculo |

## Decisões de projeto (e o porquê)

Esta seção é a parte didática: cada decisão aqui resolve um problema que aparece em sistema real.

**Dinheiro em centavos, como inteiro.** `0.1 + 0.2` em ponto flutuante dá `0.30000000000000004`. Em uma agenda que soma serviços, isso vira centavo sumindo no fechamento. Por isso `preco_centavos: 4990` significa R$ 49,90, e a API recusa `49.9`.

**O banco também valida.** Duração positiva e preço não negativo são validados pelo Pydantic (erro amigável) **e** por `CHECK` no PostgreSQL. A API pode ter bug; um script de importação pode pular a API. A restrição no banco é a última linha de defesa.

**Unicidade garantida pelo banco, não por um `SELECT` antes do `INSERT`.** Verificar "já existe este e-mail?" e depois inserir abre uma janela em que duas requisições simultâneas passam pela verificação. A restrição `UNIQUE` fecha essa janela; a API captura o `IntegrityError`, lê o **nome da restrição** (por isso a convenção de nomes em `agenda/modelos.py`) e devolve um `409` com mensagem clara em vez de um `500`.

**E-mail em minúsculas.** `Ana@Exemplo.com` e `ana@exemplo.com` são a mesma caixa postal na prática. Normalizar na entrada evita duplicidade e simplifica a busca.

**`PATCH` de verdade.** Campo omitido = não mexer; campo com `null` = apagar (quando o campo é opcional, como o telefone). Campo obrigatório com `null` é recusado com `422`. Isso é feito com `model_fields_set` do Pydantic e `model_dump(exclude_unset=True)`.

**`PUT` para o vínculo profissional–serviço.** Em vez de "adicionar um" e "remover um", o cliente envia a lista completa. A operação é idempotente (repetir dá o mesmo resultado) e, se algum serviço não existir, nada é alterado.

**Busca que trata `%` e `_` como texto.** No `LIKE`, `%` e `_` são curingas. Sem escapar, buscar `_a` encontraria "Carla". A função `_escapar_like` resolve isso.

**Testes contra PostgreSQL real, com esquema criado pelas migrações.** SQLite em memória não reproduz `ILIKE`, `CHECK` nem `ON DELETE CASCADE` do mesmo jeito. Cada teste roda dentro de uma transação desfeita no final (`join_transaction_mode="create_savepoint"`), então são rápidos e independentes. Um teste compara as migrações com os modelos: esqueceu de gerar a migração, o CI quebra.

## Estrutura

```
agenda/
  config.py        # configuração por variável de ambiente
  banco.py         # engine e sessão por requisição
  modelos.py       # tabelas (SQLAlchemy 2, Mapped[...])
  esquemas.py      # entrada e saída (Pydantic v2)
  principal.py     # cria o app FastAPI
  rotas/           # um arquivo por recurso + comum.py (404, 409)
migracoes/         # Alembic
tests/             # pytest contra PostgreSQL
```

## Tecnologias

Python · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · Docker Compose · pytest · GitHub Actions

## Autor

**Euller Pinheiro**, Diretor Técnico da [ESX Tecnologia](https://esxtecnologia.com) — desenvolvimento de sistemas, infraestrutura e TI gerenciada em São Paulo.

---

<a name="english"></a>
## English

Service-scheduling REST API built with FastAPI, SQLAlchemy and PostgreSQL. Its core is a well-tested double-booking rule; also JWT auth, queued e-mail reminders and OpenAPI docs. Work in progress — built in small, tested increments.

This first increment ships the project skeleton and CRUD for professionals, services and clients, plus the professional–service link. Money is stored as integer cents, uniqueness is enforced by the database and surfaced as `409`, `PATCH` distinguishes omitted from `null`, and tests run against a real PostgreSQL with the schema built from Alembic migrations. Run it with `docker compose up --build` and open `/docs`. Licensed under [MIT](LICENSE).
