"""Formatos de entrada e saída da API (validação feita pelo Pydantic).

Cada recurso tem três esquemas:
- `...Criar`: corpo do POST, com os campos obrigatórios;
- `...Atualizar`: corpo do PATCH, tudo opcional (só muda o que foi enviado);
- `...Ler`: o que a API devolve.
"""

import re
from datetime import datetime
from typing import Annotated, ClassVar, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

Nome = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Email = Annotated[EmailStr, AfterValidator(str.lower)]
DuracaoMinutos = Annotated[int, Field(ge=1, le=1440, description="De 1 minuto a 24 horas")]
PrecoCentavos = Annotated[int, Field(ge=0, description="Valor em centavos: 4990 = R$ 49,90")]


def _normalizar_telefone(valor: str) -> str:
    """Aceita '(11) 98765-4321', '11 3333-4444' etc. e guarda só os dígitos."""
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) not in (10, 11):
        raise ValueError("telefone deve ter DDD + número (10 ou 11 dígitos)")
    if digitos[0] == "0" or digitos[1] == "0":
        raise ValueError("DDD inválido")
    if len(digitos) == 11 and digitos[2] != "9":
        raise ValueError("celular com 11 dígitos deve começar com 9 depois do DDD")
    return digitos


Telefone = Annotated[str, AfterValidator(_normalizar_telefone)]


class _Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _Atualizacao(_Entrada):
    """No PATCH, omitir um campo é "não mexer"; mandar `null` é "apagar".

    Campos que não podem ficar vazios recusam `null` explicitamente.
    """

    _nao_anulaveis: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _recusar_nulos(self) -> Self:
        for campo in self._nao_anulaveis & self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError(f"o campo '{campo}' não pode ser nulo")
        return self


class _Saida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
    atualizado_em: datetime


# --- Serviço ---------------------------------------------------------------


class ServicoCriar(_Entrada):
    nome: Nome
    descricao: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None = (
        None
    )
    duracao_minutos: DuracaoMinutos
    preco_centavos: PrecoCentavos
    ativo: bool = True


class ServicoAtualizar(_Atualizacao):
    _nao_anulaveis = frozenset({"nome", "duracao_minutos", "preco_centavos", "ativo"})

    nome: Nome | None = None
    descricao: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None = (
        None
    )
    duracao_minutos: DuracaoMinutos | None = None
    preco_centavos: PrecoCentavos | None = None
    ativo: bool | None = None


class ServicoLer(_Saida):
    nome: str
    descricao: str | None
    duracao_minutos: int
    preco_centavos: int
    ativo: bool


# --- Profissional ----------------------------------------------------------


class ProfissionalCriar(_Entrada):
    nome: Nome
    email: Email
    ativo: bool = True


class ProfissionalAtualizar(_Atualizacao):
    _nao_anulaveis = frozenset({"nome", "email", "ativo"})

    nome: Nome | None = None
    email: Email | None = None
    ativo: bool | None = None


class ProfissionalLer(_Saida):
    nome: str
    email: str
    ativo: bool
