from typing import Any

import pytest
from fastapi.testclient import TestClient

CARLA = {"nome": "Carla Dias", "email": "carla@exemplo.com", "telefone": "(11) 98765-4321"}


def criar(cliente_http: TestClient, **extra: Any) -> dict[str, Any]:
    resposta = cliente_http.post("/clientes", json=CARLA | extra)
    assert resposta.status_code == 201, resposta.text
    corpo: dict[str, Any] = resposta.json()
    return corpo


def test_cria_cliente_guardando_so_os_digitos_do_telefone(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    assert criado["telefone"] == "11987654321"
    assert criado["email"] == "carla@exemplo.com"


def test_cliente_so_com_nome(cliente_http: TestClient) -> None:
    resposta = cliente_http.post("/clientes", json={"nome": "Davi"})
    assert resposta.status_code == 201
    assert resposta.json()["email"] is None
    assert resposta.json()["telefone"] is None


def test_varios_clientes_sem_email_nao_conflitam(cliente_http: TestClient) -> None:
    # UNIQUE no PostgreSQL ignora NULL: dois clientes sem e-mail são permitidos.
    assert cliente_http.post("/clientes", json={"nome": "Davi"}).status_code == 201
    assert cliente_http.post("/clientes", json={"nome": "Elisa"}).status_code == 201


def test_email_repetido_devolve_409(cliente_http: TestClient) -> None:
    criar(cliente_http)
    resposta = cliente_http.post("/clientes", json={"nome": "Outra", "email": "CARLA@exemplo.com"})
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe um cliente com este e-mail."


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("11 3333-4444", "1133334444"),
        ("(21)99876-5432", "21998765432"),
        ("11.98765.4321", "11987654321"),
    ],
)
def test_aceita_telefones_em_varios_formatos(
    cliente_http: TestClient, entrada: str, esperado: str
) -> None:
    resposta = cliente_http.post("/clientes", json={"nome": "Fábio", "telefone": entrada})
    assert resposta.status_code == 201
    assert resposta.json()["telefone"] == esperado


@pytest.mark.parametrize(
    "telefone",
    [
        "98765-4321",  # sem DDD
        "011 98765-4321",  # zero na frente do DDD
        "10 3333-4444",  # DDD com zero
        "11 88765-4321",  # 11 dígitos sem o 9 do celular
        "11 98765-43210",  # dígitos demais
        "telefone",
    ],
)
def test_recusa_telefone_invalido(cliente_http: TestClient, telefone: str) -> None:
    resposta = cliente_http.post("/clientes", json={"nome": "Fábio", "telefone": telefone})
    assert resposta.status_code == 422


def test_busca_por_trecho_do_nome_ou_email_sem_diferenciar_caixa(
    cliente_http: TestClient,
) -> None:
    criar(cliente_http)
    criar(cliente_http, nome="Gustavo Reis", email="gu@outro.com", telefone=None)
    criar(cliente_http, nome="Helena Carvalho", email=None, telefone=None)

    def nomes(busca: str) -> list[str]:
        return [c["nome"] for c in cliente_http.get("/clientes", params={"busca": busca}).json()]

    assert nomes("CAR") == ["Carla Dias", "Helena Carvalho"]
    assert nomes("outro.com") == ["Gustavo Reis"]
    assert nomes("zz") == []


def test_busca_trata_curingas_como_texto(cliente_http: TestClient) -> None:
    criar(cliente_http)
    criar(cliente_http, nome="Ivo 100%", email=None, telefone=None)
    resposta = cliente_http.get("/clientes", params={"busca": "0%"})
    assert [c["nome"] for c in resposta.json()] == ["Ivo 100%"]
    resposta = cliente_http.get("/clientes", params={"busca": "_a"})
    assert resposta.json() == []


def test_busca_curta_demais_devolve_422(cliente_http: TestClient) -> None:
    assert cliente_http.get("/clientes", params={"busca": "a"}).status_code == 422


def test_patch_remove_telefone_com_null(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    resposta = cliente_http.patch(f"/clientes/{criado['id']}", json={"telefone": None})
    assert resposta.status_code == 200
    assert resposta.json()["telefone"] is None
    assert resposta.json()["email"] == CARLA["email"]


def test_exclui_cliente(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    assert cliente_http.delete(f"/clientes/{criado['id']}").status_code == 204
    assert cliente_http.delete(f"/clientes/{criado['id']}").status_code == 404
