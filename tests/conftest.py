"""Fixtures de teste contra um PostgreSQL real.

Cada teste roda dentro de uma transação que é desfeita no final, então os
testes não deixam lixo no banco e podem rodar em qualquer ordem.
"""

import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.orm import Session

from agenda.banco import obter_sessao
from agenda.principal import app

URL_TESTE = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://agenda:agenda@localhost:5432/agenda_test"
)


def config_alembic() -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", URL_TESTE)
    return config


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    # O esquema dos testes nasce das migrações, não de create_all(): assim
    # uma migração quebrada derruba o CI antes de chegar em produção.
    config = config_alembic()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(URL_TESTE)
    yield engine
    engine.dispose()


@pytest.fixture
def conexao(engine: Engine) -> Iterator[Connection]:
    with engine.connect() as conexao:
        transacao = conexao.begin()
        yield conexao
        transacao.rollback()


@pytest.fixture
def sessao(conexao: Connection) -> Iterator[Session]:
    # "create_savepoint": o commit() feito pelas rotas vira um SAVEPOINT,
    # e o rollback da fixture `conexao` desfaz tudo no fim do teste.
    with Session(bind=conexao, join_transaction_mode="create_savepoint") as sessao:
        yield sessao


@pytest.fixture
def cliente_http(sessao: Session) -> Iterator[TestClient]:
    app.dependency_overrides[obter_sessao] = lambda: sessao
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
