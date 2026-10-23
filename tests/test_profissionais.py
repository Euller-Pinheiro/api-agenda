from typing import Any

import pytest
from fastapi.testclient import TestClient

ANA = {"nome": "Ana Souza", "email": "ana@exemplo.com"}


def criar(cliente_http: TestClient, **extra: Any) -> dict[str, Any]:
    resposta = cliente_http.post("/profissionais", json=ANA | extra)
    assert resposta.status_code == 201, resposta.text
    corpo: dict[str, Any] = resposta.json()
    return corpo


def test_cria_profissional_com_email_em_minusculas(cliente_http: TestClient) -> None:
    criado = criar(cliente_http, nome="  Ana Souza ", email="Ana@Exemplo.COM")
    assert criado["nome"] == "Ana Souza"
    assert criado["email"] == "ana@exemplo.com"
    assert criado["ativo"] is True
    assert criado["criado_em"] and criado["atualizado_em"]


def test_email_repetido_mesmo_com_outra_caixa_devolve_409(cliente_http: TestClient) -> None:
    criar(cliente_http)
    resposta = cliente_http.post("/profissionais", json=ANA | {"email": "ANA@exemplo.com"})
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe um profissional com este e-mail."


@pytest.mark.parametrize("email", ["sem-arroba", "a@", "@exemplo.com", ""])
def test_recusa_email_invalido(cliente_http: TestClient, email: str) -> None:
    resposta = cliente_http.post("/profissionais", json=ANA | {"email": email})
    assert resposta.status_code == 422


def test_lista_filtra_inativos(cliente_http: TestClient) -> None:
    criar(cliente_http)
    criar(cliente_http, nome="Bruno Lima", email="bruno@exemplo.com", ativo=False)
    todos = cliente_http.get("/profissionais").json()
    inativos = cliente_http.get("/profissionais", params={"ativo": False}).json()
    assert [p["nome"] for p in todos] == ["Ana Souza", "Bruno Lima"]
    assert [p["nome"] for p in inativos] == ["Bruno Lima"]


def test_desativa_profissional(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    resposta = cliente_http.patch(f"/profissionais/{criado['id']}", json={"ativo": False})
    assert resposta.status_code == 200
    assert resposta.json()["ativo"] is False
    assert resposta.json()["email"] == ANA["email"]


def test_patch_com_email_null_devolve_422(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    resposta = cliente_http.patch(f"/profissionais/{criado['id']}", json={"email": None})
    assert resposta.status_code == 422


def test_exclui_profissional(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    assert cliente_http.delete(f"/profissionais/{criado['id']}").status_code == 204
    resposta = cliente_http.get(f"/profissionais/{criado['id']}")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == f"Profissional {criado['id']} não encontrado."
