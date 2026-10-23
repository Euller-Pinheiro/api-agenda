"""Ponto de entrada da aplicação: `uvicorn agenda.principal:app`."""

from fastapi import FastAPI

from agenda.rotas import clientes, profissionais, servicos


def criar_app() -> FastAPI:
    app = FastAPI(
        title="API Agenda",
        version="0.1.0",
        description="Agendamento de serviços: profissionais, serviços, clientes e horários.",
    )

    @app.get("/saude", tags=["infra"], summary="Verifica se a API está no ar")
    def saude() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(clientes.router)
    app.include_router(profissionais.router)
    app.include_router(servicos.router)
    return app


app = criar_app()
