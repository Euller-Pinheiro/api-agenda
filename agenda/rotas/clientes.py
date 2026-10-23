"""CRUD de clientes: quem será atendido."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from agenda.banco import obter_sessao
from agenda.esquemas import ClienteAtualizar, ClienteCriar, ClienteLer
from agenda.modelos import Cliente
from agenda.rotas.comum import buscar_ou_404, remover, salvar

router = APIRouter(prefix="/clientes", tags=["clientes"])
SessaoDep = Annotated[Session, Depends(obter_sessao)]


def _escapar_like(texto: str) -> str:
    """Impede que '%' e '_' digitados pelo usuário virem curingas do LIKE."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("", response_model=list[ClienteLer], summary="Lista os clientes")
def listar(
    sessao: SessaoDep,
    busca: Annotated[
        str | None,
        Query(min_length=2, max_length=120, description="Trecho do nome ou do e-mail"),
    ] = None,
) -> list[Cliente]:
    consulta = select(Cliente).order_by(Cliente.nome, Cliente.id)
    if busca:
        padrao = f"%{_escapar_like(busca.strip())}%"
        consulta = consulta.where(
            or_(Cliente.nome.ilike(padrao, escape="\\"), Cliente.email.ilike(padrao, escape="\\"))
        )
    return list(sessao.scalars(consulta))


@router.post(
    "", response_model=ClienteLer, status_code=status.HTTP_201_CREATED, summary="Cria um cliente"
)
def criar(dados: ClienteCriar, sessao: SessaoDep) -> Cliente:
    cliente = Cliente(**dados.model_dump())
    salvar(sessao, cliente)
    return cliente


@router.get("/{cliente_id}", response_model=ClienteLer, summary="Detalha um cliente")
def detalhar(cliente_id: int, sessao: SessaoDep) -> Cliente:
    return buscar_ou_404(sessao, Cliente, cliente_id, "Cliente")


@router.patch("/{cliente_id}", response_model=ClienteLer, summary="Altera um cliente")
def atualizar(cliente_id: int, dados: ClienteAtualizar, sessao: SessaoDep) -> Cliente:
    cliente = buscar_ou_404(sessao, Cliente, cliente_id, "Cliente")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    salvar(sessao, cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove um cliente")
def excluir(cliente_id: int, sessao: SessaoDep) -> None:
    remover(sessao, buscar_ou_404(sessao, Cliente, cliente_id, "Cliente"))
