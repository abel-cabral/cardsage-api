from bs4 import BeautifulSoup

def purificarHTML(html):
    # Analisar o HTML com BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    
    # Remover todos os elementos <script> e <style>
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    
    # Extrair o texto limpo
    clean_text = soup.get_text(separator=' ')
    
    # Remover espaços em branco extras
    clean_text = ' '.join(clean_text.split())
    
    return clean_text


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