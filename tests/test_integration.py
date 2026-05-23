"""Testes de Integração — banco de dados real (test.db) + rotas FastAPI."""
import pytest


class TestListarProdutos:
    def test_retorna_lista_com_produtos(self, client):
        response = client.get("/api/produtos")
        assert response.status_code == 200
        dados = response.json()
        assert isinstance(dados, list)
        assert len(dados) >= 2

    def test_produtos_possuem_chaves_corretas(self, client):
        response = client.get("/api/produtos")
        produto = response.json()[0]
        assert "nome" in produto
        assert "preco" in produto
        assert "estoque" in produto

    def test_teclado_presente_na_lista(self, client):
        response = client.get("/api/produtos")
        nomes = [p["nome"] for p in response.json()]
        assert "teclado" in nomes


class TestComprarProduto:
    def test_compra_com_sucesso(self, client):
        payload = {"produto": "teclado", "cartao": "1234-5678", "cupom": ""}
        response = client.post("/api/comprar", json=payload)
        assert response.status_code == 200
        dados = response.json()
        assert dados["status"] == "sucesso"
        assert dados["valor_pago"] == 200.0

    def test_compra_com_cupom_desconto(self, client):
        payload = {"produto": "teclado", "cartao": "1234-5678", "cupom": "GEEK20"}
        response = client.post("/api/comprar", json=payload)
        assert response.status_code == 200
        assert response.json()["valor_pago"] == 160.0

    def test_produto_inexistente_retorna_404(self, client):
        payload = {"produto": "invisivel", "cartao": "1234-5678", "cupom": ""}
        response = client.post("/api/comprar", json=payload)
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_produto_sem_estoque_retorna_400(self, client_sem_estoque):
        payload = {"produto": "zerado", "cartao": "1234-5678", "cupom": ""}
        response = client_sem_estoque.post("/api/comprar", json=payload)
        assert response.status_code == 400
        assert "estoque" in response.json()["detail"].lower()

    def test_gateway_recusado_retorna_400(self, client_gateway_recusado):
        payload = {"produto": "teclado", "cartao": "1234-5678", "cupom": ""}
        response = client_gateway_recusado.post("/api/comprar", json=payload)
        assert response.status_code == 400
        assert "Gateway" in response.json()["detail"]

    def test_compra_reduz_estoque_no_banco(self, client):
        # Verifica estoque antes
        antes = client.get("/api/produtos").json()
        estoque_antes = next(p["estoque"] for p in antes if p["nome"] == "mouse")

        payload = {"produto": "mouse", "cartao": "1234-5678", "cupom": ""}
        client.post("/api/comprar", json=payload)

        depois = client.get("/api/produtos").json()
        estoque_depois = next(p["estoque"] for p in depois if p["nome"] == "mouse")

        assert estoque_depois == estoque_antes - 1

    def test_produto_case_insensitive(self, client):
        payload = {"produto": "TECLADO", "cartao": "1234-5678", "cupom": ""}
        response = client.post("/api/comprar", json=payload)
        assert response.status_code == 200


class TestFrontend:
    def test_rota_raiz_retorna_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "GeekStore" in response.text