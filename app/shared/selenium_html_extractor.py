import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .util import purificarHTML


# Configurar o driver e chrome do Selenium com opções headless
options = Options()
if (os.getenv('MODE') == 'prod'):
    options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'
    service = Service('/app/.chrome-for-testing/chromedriver-linux64/chromedriver')
else:
    service = Service(ChromeDriverManager().install())

options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

def html_extrator(url, max_retries=3, wait_time=20):
    attempt = 0
    while attempt < max_retries:
        try:
            driver.get(url)

            # Esperar que o conteúdo seja carregado, se necessário
            driver.implicitly_wait(wait_time)

            # Obter o conteúdo da página
            page_source = driver.page_source

            # Usar BeautifulSoup para processar o conteúdo
            soup = BeautifulSoup(page_source, 'html.parser')

            # Remover scripts e estilos
            for script in soup(["script", "style"]):
                script.extract()

            # Extrair o texto visível
            text = soup.get_text(separator=' ')
            return purificarHTML(text)
        except Exception as e:
            attempt += 1
            time.sleep(5)  # Esperar 5 segundos antes de tentar novamente
            print(f"Attempt {attempt} failed: {e}")

    # Fechar o driver apenas após todas as tentativas falharem
    driver.quit()
    return None

__all__ = ['html_extrator']