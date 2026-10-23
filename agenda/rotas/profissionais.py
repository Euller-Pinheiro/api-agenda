"""CRUD de profissionais: quem presta os profissionais."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agenda.banco import obter_sessao
from agenda.esquemas import ProfissionalAtualizar, ProfissionalCriar, ProfissionalLer
from agenda.modelos import Profissional
from agenda.rotas.comum import buscar_ou_404, remover, salvar

router = APIRouter(prefix="/profissionais", tags=["profissionais"])
SessaoDep = Annotated[Session, Depends(obter_sessao)]


@router.get("", response_model=list[ProfissionalLer], summary="Lista os profissionais")
def listar(sessao: SessaoDep, ativo: bool | None = None) -> list[Profissional]:
    consulta = select(Profissional).order_by(Profissional.nome)
    if ativo is not None:
        consulta = consulta.where(Profissional.ativo == ativo)
    return list(sessao.scalars(consulta))


@router.post(
    "",
    response_model=ProfissionalLer,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um profissional",
)
def criar(dados: ProfissionalCriar, sessao: SessaoDep) -> Profissional:
    profissional = Profissional(**dados.model_dump())
    salvar(sessao, profissional)
    return profissional


@router.get("/{profissional_id}", response_model=ProfissionalLer, summary="Detalha um profissional")
def detalhar(profissional_id: int, sessao: SessaoDep) -> Profissional:
    return buscar_ou_404(sessao, Profissional, profissional_id, "Profissional")


@router.patch(
    "/{profissional_id}", response_model=ProfissionalLer, summary="Altera um profissional"
)
def atualizar(
    profissional_id: int, dados: ProfissionalAtualizar, sessao: SessaoDep
) -> Profissional:
    profissional = buscar_ou_404(sessao, Profissional, profissional_id, "Profissional")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(profissional, campo, valor)
    salvar(sessao, profissional)
    return profissional


@router.delete(
    "/{profissional_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove um profissional"
)
def excluir(profissional_id: int, sessao: SessaoDep) -> None:
    remover(sessao, buscar_ou_404(sessao, Profissional, profissional_id, "Profissional"))
