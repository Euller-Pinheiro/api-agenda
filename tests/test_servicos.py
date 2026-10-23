from typing import Any

import pytest
from fastapi.testclient import TestClient

CORTE = {"nome": "Corte de cabelo", "duracao_minutos": 30, "preco_centavos": 4990}


def criar(cliente_http: TestClient, **extra: Any) -> dict[str, Any]:
    resposta = cliente_http.post("/servicos", json=CORTE | extra)
    assert resposta.status_code == 201, resposta.text
    corpo: dict[str, Any] = resposta.json()
    return corpo


def test_cria_e_detalha_servico(cliente_http: TestClient) -> None:
    criado = criar(cliente_http, descricao="  Inclui lavagem  ")
    assert criado["descricao"] == "Inclui lavagem"
    assert criado["ativo"] is True

    resposta = cliente_http.get(f"/servicos/{criado['id']}")
    assert resposta.status_code == 200
    assert resposta.json() == criado


def test_lista_em_ordem_alfabetica_e_filtra_por_ativo(cliente_http: TestClient) -> None:
    criar(cliente_http, nome="Manicure")
    criar(cliente_http, nome="Barba", ativo=False)
    criar(cliente_http)

    nomes = [s["nome"] for s in cliente_http.get("/servicos").json()]
    assert nomes == ["Barba", "Corte de cabelo", "Manicure"]

    ativos = [s["nome"] for s in cliente_http.get("/servicos", params={"ativo": True}).json()]
    assert ativos == ["Corte de cabelo", "Manicure"]


def test_nome_repetido_devolve_409(cliente_http: TestClient) -> None:
    criar(cliente_http)
    resposta = cliente_http.post("/servicos", json=CORTE)
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe um serviço com este nome."


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("duracao_minutos", 0),
        ("duracao_minutos", 1441),
        ("preco_centavos", -1),
        ("preco_centavos", 49.9),
        ("nome", "   "),
        ("nome", "x" * 121),
    ],
)
def test_recusa_valores_invalidos(cliente_http: TestClient, campo: str, valor: Any) -> None:
    resposta = cliente_http.post("/servicos", json=CORTE | {campo: valor})
    assert resposta.status_code == 422


def test_recusa_campo_desconhecido(cliente_http: TestClient) -> None:
    resposta = cliente_http.post("/servicos", json=CORTE | {"preco": 10})
    assert resposta.status_code == 422


def test_patch_altera_so_o_que_foi_enviado(cliente_http: TestClient) -> None:
    criado = criar(cliente_http, descricao="Com lavagem")
    resposta = cliente_http.patch(f"/servicos/{criado['id']}", json={"preco_centavos": 5500})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["preco_centavos"] == 5500
    assert corpo["descricao"] == "Com lavagem"
    assert corpo["duracao_minutos"] == 30


def test_patch_com_null_apaga_campo_opcional(cliente_http: TestClient) -> None:
    criado = criar(cliente_http, descricao="Com lavagem")
    resposta = cliente_http.patch(f"/servicos/{criado['id']}", json={"descricao": None})
    assert resposta.status_code == 200
    assert resposta.json()["descricao"] is None


def test_patch_com_null_em_campo_obrigatorio_devolve_422(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    resposta = cliente_http.patch(f"/servicos/{criado['id']}", json={"nome": None})
    assert resposta.status_code == 422
    assert "não pode ser nulo" in resposta.text


def test_patch_para_nome_de_outro_servico_devolve_409(cliente_http: TestClient) -> None:
    criar(cliente_http)
    outro = criar(cliente_http, nome="Barba")
    resposta = cliente_http.patch(f"/servicos/{outro['id']}", json={"nome": CORTE["nome"]})
    assert resposta.status_code == 409


def test_exclui_servico(cliente_http: TestClient) -> None:
    criado = criar(cliente_http)
    assert cliente_http.delete(f"/servicos/{criado['id']}").status_code == 204
    assert cliente_http.get(f"/servicos/{criado['id']}").status_code == 404


@pytest.mark.parametrize("metodo", ["get", "patch", "delete"])
def test_servico_inexistente_devolve_404(cliente_http: TestClient, metodo: str) -> None:
    kwargs: dict[str, Any] = {"json": {}} if metodo == "patch" else {}
    resposta = cliente_http.request(metodo.upper(), "/servicos/999999", **kwargs)
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Serviço 999999 não encontrado."
