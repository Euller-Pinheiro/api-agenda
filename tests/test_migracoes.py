"""As migrações precisam bater com os modelos e ser reversíveis."""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, inspect

from agenda.modelos import Base
from tests.conftest import config_alembic


def test_migracoes_refletem_os_modelos(engine: Engine) -> None:
    with engine.connect() as conexao:
        diferencas = compare_metadata(MigrationContext.configure(conexao), Base.metadata)
    assert diferencas == [], "rode `alembic revision --autogenerate` e revise a migração"


def test_migracoes_descem_e_sobem(engine: Engine) -> None:
    config = config_alembic()
    command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
    command.upgrade(config, "head")
    assert {"profissional", "servico", "cliente", "profissional_servico"} <= set(
        inspect(engine).get_table_names()
    )
