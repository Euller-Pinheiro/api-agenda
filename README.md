# api-agenda

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-C9A84C)
![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

**[English below](#english)**

API REST de **agendamento de serviços** — profissionais, serviços, clientes e horários — construída com **FastAPI, SQLAlchemy e PostgreSQL**.

## Por que este projeto

Agenda parece simples até aparecerem os casos reais: dois atendimentos que se sobrepõem por um minuto, o profissional que muda a disponibilidade, o fuso horário, o lembrete que precisa sair mesmo se o servidor reiniciar. O coração deste projeto é a regra de conflito de horários, coberta por testes contra um banco PostgreSQL de verdade.

## O que está a caminho

O projeto está sendo construído em entregas pequenas, cada uma com testes e CI. Acompanhe pelos commits e pull requests.

- [ ] Estrutura do projeto e cadastros de profissionais, serviços e clientes
- [ ] Disponibilidade semanal e detecção de conflito de horários
- [ ] Autenticação com JWT e perfis de acesso
- [ ] Lembretes por e-mail em fila
- [ ] Paginação, filtros e erros padronizados

## Tecnologias

Python · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · Docker Compose · pytest · GitHub Actions

## Autor

**Euller Pinheiro**, Diretor Técnico da [ESX Tecnologia](https://esxtecnologia.com) — desenvolvimento de sistemas, infraestrutura e TI gerenciada em São Paulo.

---

<a name="english"></a>
## English

Service-scheduling REST API built with FastAPI, SQLAlchemy and PostgreSQL. Its core is a well-tested double-booking rule; also JWT auth, queued e-mail reminders and OpenAPI docs. Work in progress — built in small, tested increments. Licensed under [MIT](LICENSE).
