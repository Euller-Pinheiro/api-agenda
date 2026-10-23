"""Quais serviços cada profissional atende."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


def _post(cliente_http: TestClient, caminho: str, corpo: dict[str, Any]) -> int:
    resposta = cliente_http.post(caminho, json=corpo)
    assert resposta.status_code == 201, resposta.text
    id_: int = resposta.json()["id"]
    return id_


@pytest.fixture
def ids(cliente_http: TestClient) -> dict[str, int]:
    def servico(nome: str) -> int:
        corpo = {"nome": nome, "duracao_minutos": 30, "preco_centavos": 3000}
        return _post(cliente_http, "/servicos", corpo)

    def profissional(nome: str, email: str, ativo: bool = True) -> int:
        corpo = {"nome": nome, "email": email, "ativo": ativo}
        return _post(cliente_http, "/profissionais", corpo)

    return {
        "corte": servico("Corte"),
        "barba": servico("Barba"),
        "ana": profissional("Ana", "ana@exemplo.com"),
        "bruno": profissional("Bruno", "bruno@exemplo.com", ativo=False),
    }


def _nomes(resposta: Any) -> list[str]:
    assert resposta.status_code == 200, resposta.text
    return [item["nome"] for item in resposta.json()]


def test_profissional_novo_nao_atende_nada(cliente_http: TestClient, ids: dict[str, int]) -> None:
    assert _nomes(cliente_http.get(f"/profissionais/{ids['ana']}/servicos")) == []


def test_define_e_substitui_servicos(cliente_http: TestClient, ids: dict[str, int]) -> None:
    url = f"/profissionais/{ids['ana']}/servicos"
    # IDs repetidos são aceitos e contados uma vez só.
    resposta = cliente_http.put(
        url, json={"servico_ids": [ids["corte"], ids["barba"], ids["corte"]]}
    )
    assert _nomes(resposta) == ["Barba", "Corte"]

    assert _nomes(cliente_http.put(url, json={"servico_ids": [ids["corte"]]})) == ["Corte"]
    assert _nomes(cliente_http.get(url)) == ["Corte"]

    assert _nomes(cliente_http.put(url, json={"servico_ids": []})) == []


def test_servico_inexistente_nao_altera_nada(cliente_http: TestClient, ids: dict[str, int]) -> None:
    url = f"/profissionais/{ids['ana']}/servicos"
    cliente_http.put(url, json={"servico_ids": [ids["corte"]]})

    resposta = cliente_http.put(url, json={"servico_ids": [ids["barba"], 999998, 999999]})
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Serviços inexistentes: 999998, 999999."
    assert _nomes(cliente_http.get(url)) == ["Corte"]


def test_profissional_inexistente_devolve_404(cliente_http: TestClient) -> None:
    resposta = cliente_http.put("/profissionais/999999/servicos", json={"servico_ids": []})
    assert resposta.status_code == 404


def test_lista_profissionais_do_servico(cliente_http: TestClient, ids: dict[str, int]) -> None:
    for pessoa in ("ana", "bruno"):
        cliente_http.put(
            f"/profissionais/{ids[pessoa]}/servicos", json={"servico_ids": [ids["corte"]]}
        )
    url = f"/servicos/{ids['corte']}/profissionais"
    assert _nomes(cliente_http.get(url)) == ["Ana", "Bruno"]
    assert _nomes(cliente_http.get(url, params={"ativo": True})) == ["Ana"]
    assert _nomes(cliente_http.get(f"/servicos/{ids['barba']}/profissionais")) == []
    assert cliente_http.get("/servicos/999999/profissionais").status_code == 404


def test_excluir_servico_remove_o_vinculo(cliente_http: TestClient, ids: dict[str, int]) -> None:
    url = f"/profissionais/{ids['ana']}/servicos"
    cliente_http.put(url, json={"servico_ids": [ids["corte"], ids["barba"]]})
    assert cliente_http.delete(f"/servicos/{ids['barba']}").status_code == 204
    assert _nomes(cliente_http.get(url)) == ["Corte"]
