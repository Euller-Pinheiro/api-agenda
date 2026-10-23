"""Ambiente do Alembic: usa a mesma configuração e os mesmos modelos da API."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from agenda.config import obter_configuracao

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Quem chama (por exemplo, os testes) pode passar outra URL via `sqlalchemy.url`.
url = config.get_main_option("sqlalchemy.url") or obter_configuracao().database_url

target_metadata = None


def rodar_offline() -> None:
    """Gera o SQL sem conectar (`alembic upgrade head --sql`)."""
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def rodar_online() -> None:
    engine = create_engine(url)
    with engine.connect() as conexao:
        context.configure(connection=conexao, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    rodar_offline()
else:
    rodar_online()
