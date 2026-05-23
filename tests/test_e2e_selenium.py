"""Testes End-to-End com Selenium — roda em modo headless para CI."""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:8000"


def criar_driver():
    """Cria um driver Chrome headless compatível com CI."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception:
        return webdriver.Chrome(options=options)


@pytest.fixture(scope="module")
def driver():
    d = criar_driver()
    yield d
    d.quit()


class TestE2ECompra:
    def test_pagina_carrega_com_titulo(self, driver):
        driver.get(BASE_URL)
        assert "GeekStore" in driver.title

    def test_compra_teclado_exibe_mensagem_sucesso(self, driver):
        driver.get(BASE_URL)

        driver.find_element(By.ID, "input-produto").clear()
        driver.find_element(By.ID, "input-produto").send_keys("teclado")

        driver.find_element(By.ID, "input-cartao").clear()
        driver.find_element(By.ID, "input-cartao").send_keys("1234-5678-9012-3456")

        driver.find_element(By.ID, "btn-comprar").click()

        # Aguarda a mensagem de resultado (tem delay de 1.5s no JS)
        msg_div = WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "mensagem"), "aprovada"
            )
        )
        mensagem = driver.find_element(By.ID, "mensagem").text
        assert "aprovada" in mensagem.lower() or "R$" in mensagem

    def test_compra_com_cupom_exibe_valor_com_desconto(self, driver):
        driver.get(BASE_URL)

        driver.find_element(By.ID, "input-produto").send_keys("mouse")
        driver.find_element(By.ID, "input-cartao").send_keys("9999-8888-7777-6666")
        driver.find_element(By.ID, "input-cupom").send_keys("GEEK20")

        driver.find_element(By.ID, "btn-comprar").click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "mensagem"), "80.00"
            )
        )
        mensagem = driver.find_element(By.ID, "mensagem").text
        assert "80.00" in mensagem

    def test_produto_inexistente_exibe_erro(self, driver):
        driver.get(BASE_URL)

        driver.find_element(By.ID, "input-produto").send_keys("produto_fantasma")
        driver.find_element(By.ID, "input-cartao").send_keys("0000-0000-0000-0000")

        driver.find_element(By.ID, "btn-comprar").click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "mensagem"), "Erro"
            )
        )
        mensagem = driver.find_element(By.ID, "mensagem").text
        assert "Erro" in mensagem