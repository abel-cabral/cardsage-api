import requests
from bs4 import BeautifulSoup
from .util import purificarHTML

def html_extrator(url, max_retries=3, wait_time=20):
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(url, timeout=wait_time)
            response.raise_for_status()  # Lanza una excepción para respuestas no exitosas

            # Usar BeautifulSoup para procesar el contenido
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remover scripts y estilos
            for script in soup(["script", "style"]):
                script.extract()

            # Extraer el texto visible
            text = soup.get_text(separator=' ')
            return purificarHTML(text)
        except Exception as e:
            attempt += 1
            time.sleep(5)  # Esperar 5 segundos antes de intentar nuevamente
            print(f"Intento {attempt} fallido: {e}")

    return None

__all__ = ['html_extrator']