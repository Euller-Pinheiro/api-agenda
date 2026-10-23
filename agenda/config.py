"""Configuração lida de variáveis de ambiente (ou de um arquivo .env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    """Valores que mudam entre máquinas: nunca ficam fixos no código."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://agenda:agenda@localhost:5432/agenda"
    sql_echo: bool = False


@lru_cache
def obter_configuracao() -> Configuracao:
    return Configuracao()
