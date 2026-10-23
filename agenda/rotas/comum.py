"""Peças reaproveitadas pelas rotas: buscar por id e gravar com segurança."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agenda.modelos import Base

# Restrição do banco -> mensagem para quem usa a API. Deixar o banco garantir a
# unicidade (em vez de um SELECT antes do INSERT) evita a corrida entre duas
# requisições simultâneas com o mesmo e-mail.
MENSAGENS_RESTRICAO = {
    "uq_profissional_email": "Já existe um profissional com este e-mail.",
    "uq_servico_nome": "Já existe um serviço com este nome.",
    "uq_cliente_email": "Já existe um cliente com este e-mail.",
}


def buscar_ou_404[M: Base](sessao: Session, modelo: type[M], id_: int, rotulo: str) -> M:
    objeto = sessao.get(modelo, id_)
    if objeto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{rotulo} {id_} não encontrado.")
    return objeto


def _nome_restricao(erro: IntegrityError) -> str | None:
    diagnostico = getattr(erro.orig, "diag", None)
    return getattr(diagnostico, "constraint_name", None)


def salvar(sessao: Session, objeto: Base) -> None:
    """Grava o objeto; violação de unicidade vira HTTP 409 em vez de erro 500."""
    sessao.add(objeto)
    try:
        sessao.commit()
    except IntegrityError as erro:
        sessao.rollback()
        mensagem = MENSAGENS_RESTRICAO.get(
            _nome_restricao(erro) or "", "Os dados conflitam com um registro existente."
        )
        raise HTTPException(status.HTTP_409_CONFLICT, mensagem) from erro
    sessao.refresh(objeto)


def remover(sessao: Session, objeto: Base) -> None:
    sessao.delete(objeto)
    sessao.commit()
