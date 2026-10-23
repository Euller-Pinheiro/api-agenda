from fastapi.testclient import TestClient


def test_saude_responde_ok(cliente_http: TestClient) -> None:
    resposta = cliente_http.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_documentacao_openapi_disponivel(cliente_http: TestClient) -> None:
    resposta = cliente_http.get("/openapi.json")
    assert resposta.status_code == 200
    assert resposta.json()["info"]["title"] == "API Agenda"
