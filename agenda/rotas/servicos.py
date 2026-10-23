"""CRUD de serviços: o que é oferecido, quanto dura e quanto custa."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agenda.banco import obter_sessao
from agenda.esquemas import ServicoAtualizar, ServicoCriar, ServicoLer
from agenda.modelos import Servico
from agenda.rotas.comum import buscar_ou_404, remover, salvar

router = APIRouter(prefix="/servicos", tags=["serviços"])
SessaoDep = Annotated[Session, Depends(obter_sessao)]


@router.get("", response_model=list[ServicoLer], summary="Lista os serviços")
def listar(sessao: SessaoDep, ativo: bool | None = None) -> list[Servico]:
    consulta = select(Servico).order_by(Servico.nome)
    if ativo is not None:
        consulta = consulta.where(Servico.ativo == ativo)
    return list(sessao.scalars(consulta))


@router.post(
    "", response_model=ServicoLer, status_code=status.HTTP_201_CREATED, summary="Cria um serviço"
)
def criar(dados: ServicoCriar, sessao: SessaoDep) -> Servico:
    servico = Servico(**dados.model_dump())
    salvar(sessao, servico)
    return servico


@router.get("/{servico_id}", response_model=ServicoLer, summary="Detalha um serviço")
def detalhar(servico_id: int, sessao: SessaoDep) -> Servico:
    return buscar_ou_404(sessao, Servico, servico_id, "Serviço")


@router.patch("/{servico_id}", response_model=ServicoLer, summary="Altera um serviço")
def atualizar(servico_id: int, dados: ServicoAtualizar, sessao: SessaoDep) -> Servico:
    servico = buscar_ou_404(sessao, Servico, servico_id, "Serviço")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(servico, campo, valor)
    salvar(sessao, servico)
    return servico


@router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove um serviço")
def excluir(servico_id: int, sessao: SessaoDep) -> None:
    remover(sessao, buscar_ou_404(sessao, Servico, servico_id, "Serviço"))
