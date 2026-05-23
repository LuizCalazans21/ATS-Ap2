"""Testes de Unidade — regras de negócio puras (sem I/O)."""
import pytest
from unittest.mock import MagicMock

from main import calcular_desconto, processar_pedido, GatewayPagamento


class TestCalcularDesconto:
    def test_cupom_valido_aplica_20_porcento(self):
        resultado = calcular_desconto(200.0, "GEEK20")
        assert resultado == 160.0

    def test_cupom_invalido_nao_aplica_desconto(self):
        resultado = calcular_desconto(200.0, "INVALIDO")
        assert resultado == 200.0

    def test_cupom_vazio_nao_aplica_desconto(self):
        resultado = calcular_desconto(100.0, "")
        assert resultado == 100.0

    def test_desconto_com_valor_fracionado(self):
        resultado = calcular_desconto(99.99, "GEEK20")
        assert round(resultado, 2) == 79.99


class TestProcessarPedido:
    def test_sucesso_com_gateway_aprovado(self):
        gateway = MagicMock()
        gateway.cobrar.return_value = True

        resultado = processar_pedido(100.0, "1234-5678", gateway)

        assert resultado == "Compra aprovada!"
        gateway.cobrar.assert_called_once_with("1234-5678", 100.0)

    def test_valor_zero_levanta_value_error(self):
        gateway = MagicMock()

        with pytest.raises(ValueError, match="O valor deve ser maior que zero"):
            processar_pedido(0, "1234-5678", gateway)

        gateway.cobrar.assert_not_called()

    def test_valor_negativo_levanta_value_error(self):
        gateway = MagicMock()

        with pytest.raises(ValueError):
            processar_pedido(-10.0, "1234-5678", gateway)

    def test_gateway_recusa_levanta_value_error(self):
        gateway = MagicMock()
        gateway.cobrar.return_value = False

        with pytest.raises(ValueError, match="Pagamento recusado pelo Gateway"):
            processar_pedido(100.0, "1234-5678", gateway)

    def test_gateway_cobrar_chamado_com_argumentos_corretos(self):
        gateway = MagicMock()
        gateway.cobrar.return_value = True

        processar_pedido(250.0, "9999-0000", gateway)

        gateway.cobrar.assert_called_once_with("9999-0000", 250.0)

    def test_gateway_real_retorna_true(self):
        gateway = GatewayPagamento()
        resultado = gateway.cobrar("1234", 100.0)
        assert resultado is True