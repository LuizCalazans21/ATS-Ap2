import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

TEST_DB = "test_geekstore.db"
os.environ["DB_PATH"] = TEST_DB

from main import app, get_gateway, GatewayPagamento  # noqa: E402


def criar_banco(produtos_extras=None):
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE produtos (nome TEXT PRIMARY KEY, preco REAL, estoque INTEGER)"
    )
    conn.execute("INSERT INTO produtos VALUES ('teclado', 200.0, 10)")
    conn.execute("INSERT INTO produtos VALUES ('mouse', 100.0, 5)")
    if produtos_extras:
        for p in produtos_extras:
            conn.execute("INSERT INTO produtos VALUES (?, ?, ?)", p)
    conn.commit()
    conn.close()


@pytest.fixture()
def db():
    criar_banco()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture()
def db_sem_estoque():
    criar_banco(produtos_extras=[("zerado", 50.0, 0)])
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture()
def client(db):
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def client_sem_estoque(db_sem_estoque):
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def client_gateway_recusado(db):
    class GatewayRecusado:
        def cobrar(self, cartao: str, valor: float):
            return False

    app.dependency_overrides[get_gateway] = lambda: GatewayRecusado()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()