import requests
from bs4 import BeautifulSoup
from .util import purificarHTML

# Função para extrair texto de uma página web
def html_extrator(url):
    try:
        # Definir um User-Agent para a requisição
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Fazer a requisição GET para a URL
        response = requests.get(url, headers=headers)
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
    except requests.RequestException as e:
        return f'Erro ao acessar a página: {e}'
    
    # Analisar o HTML da página com BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remover todos os scripts e estilos
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Extrair o texto visível
    texto_visivel = soup.get_text(separator=' ', strip=True)
    
    return purificarHTML(texto_visivel)

__all__ = ['html_extrator']