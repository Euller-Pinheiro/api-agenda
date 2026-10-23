"""Conexão com o PostgreSQL e sessão por requisição."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from agenda.config import obter_configuracao

_config = obter_configuracao()

engine = create_engine(_config.database_url, echo=_config.sql_echo, pool_pre_ping=True)
FabricaSessao = sessionmaker(bind=engine, expire_on_commit=False)


def obter_sessao() -> Iterator[Session]:
    """Dependência do FastAPI: abre uma sessão e garante o fechamento."""
    with FabricaSessao() as sessao:
        yield sessao
