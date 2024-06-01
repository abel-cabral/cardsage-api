import re

def purificarHTML(html):
    text = re.sub(r'\s+', ' ', html) # Remove múltiplos espaços, novas linhas e tabulações
    text = text.strip() # Remove espaços no início e no fim do texto
    return text

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