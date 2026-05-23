"""Step definitions para o arquivo compra.feature."""
import os
import sqlite3
import pytest
from pytest_bdd import given, when, then, parsers, scenario
from fastapi.testclient import TestClient

TEST_DB = "test_bdd.db"
os.environ["DB_PATH"] = TEST_DB

from main import app  # noqa: E402

FEATURE_FILE = os.path.join(os.path.dirname(__file__), "../features/compra.feature")


# ── Cenários vinculados ao arquivo .feature ────────────────────────────────────
@scenario(FEATURE_FILE, "Compra com sucesso sem cupom")
def test_compra_sucesso_sem_cupom():
    pass


@scenario(FEATURE_FILE, "Compra com sucesso usando cupom GEEK20")
def test_compra_sucesso_com_cupom():
    pass


@scenario(FEATURE_FILE, "Tentativa de compra de produto sem estoque")
def test_compra_sem_estoque():
    pass


# ── Fixtures compartilhadas ────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def setup_banco():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    conn.execute(
        "CREATE TABLE produtos (nome TEXT PRIMARY KEY, preco REAL, estoque INTEGER)"
    )
    conn.execute("INSERT INTO produtos VALUES ('teclado', 200.0, 10)")
    conn.execute("INSERT INTO produtos VALUES ('mouse', 100.0, 5)")
    conn.execute("INSERT INTO produtos VALUES ('sem_estoque', 50.0, 0)")
    conn.commit()
    conn.close()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture()
def contexto():
    return {}


# ── Steps: Dado ────────────────────────────────────────────────────────────────
@given(parsers.parse('que o produto "{nome}" está disponível no estoque'))
def produto_disponivel(nome, contexto):
    contexto["produto"] = nome


@given(parsers.parse('que o produto "{nome}" não possui estoque'))
def produto_sem_estoque(nome, contexto):
    contexto["produto"] = nome


# ── Steps: Quando ──────────────────────────────────────────────────────────────
@when(parsers.parse('eu realizo a compra do produto "{produto}" com o cartão "{cartao}" sem cupom'))
def realizar_compra_sem_cupom(produto, cartao, contexto):
    with TestClient(app) as client:
        response = client.post(
            "/api/comprar",
            json={"produto": produto, "cartao": cartao, "cupom": ""},
        )
    contexto["response"] = response


@when(parsers.parse('eu realizo a compra do produto "{produto}" com o cartão "{cartao}" e o cupom "{cupom}"'))
def realizar_compra_com_cupom(produto, cartao, cupom, contexto):
    with TestClient(app) as client:
        response = client.post(
            "/api/comprar",
            json={"produto": produto, "cartao": cartao, "cupom": cupom},
        )
    contexto["response"] = response


# ── Steps: Então ───────────────────────────────────────────────────────────────
@then("a compra é aprovada com sucesso")
def compra_aprovada(contexto):
    assert contexto["response"].status_code == 200
    assert contexto["response"].json()["status"] == "sucesso"


@then(parsers.parse("o valor pago é {valor:f}"))
def valor_pago(valor, contexto):
    assert contexto["response"].json()["valor_pago"] == pytest.approx(valor)


@then("a compra é recusada com erro de estoque")
def compra_recusada_estoque(contexto):
    assert contexto["response"].status_code == 400
    assert "estoque" in contexto["response"].json()["detail"].lower()