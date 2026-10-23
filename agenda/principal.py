"""Ponto de entrada da aplicação: `uvicorn agenda.principal:app`."""

from fastapi import FastAPI


def criar_app() -> FastAPI:
    app = FastAPI(
        title="API Agenda",
        version="0.1.0",
        description="Agendamento de serviços: profissionais, serviços, clientes e horários.",
    )

    @app.get("/saude", tags=["infra"], summary="Verifica se a API está no ar")
    def saude() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = criar_app()
