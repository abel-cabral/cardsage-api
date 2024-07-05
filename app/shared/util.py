import html2text
import re

from bs4 import BeautifulSoup

def purificarHTML(html):
    # Parseia o HTML com BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove elementos indesejados como scripts, estilos, links, etc.
    for script in soup(['script', 'style', 'a', 'link', 'head', 'title', 'meta']):
        script.extract()

    # Obtém o texto limpo usando html2text
    h = html2text.HTML2Text()
    h.ignore_links = True  # Ignora links
    h.ignore_images = True  # Ignora imagens
    h.ignore_emphasis = True  # Ignora ênfase (como negrito e itálico)

    # Extrai o texto legível
    texto_extraido = h.handle(soup.get_text())

    # Remove caracteres indesejados e espaços extras
    texto_limpo = ' '.join(texto_extraido.split())

    return texto_limpo


def partirHTML(text, max_length=2000):
    segments = []
    if len(text) <= max_length:
        return [text]
    
    while len(text) > max_length:
        split_index = text.rfind(' ', 0, max_length)  # Encontra o último espaço dentro do limite de caracteres
        if split_index == -1:
            split_index = max_length
        segments.append(text[:split_index])
        text = text[split_index:].strip()
    segments.append(text)
    return segments

__all__ = ['partirHTML', 'purificarHTML']