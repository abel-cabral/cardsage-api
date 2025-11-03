import os
import json
import aiohttp
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configurações da LLaMA local
LLAMA_API_URL = "http://192.168.1.117:11434/api/generate"
LLAMA_MODEL = "gemma:2b"

# Lista de tags iniciais
taglist = os.getenv('TAGLIST').split(',')

# Prompt principal — geração de resumo, título e tags
promptIntroducao = f"""
Você receberá um texto representado como tokens.
Sua tarefa é:

1. Resumir o conteúdo de forma clara e objetiva, SEMPRE em terceira pessoa
   (ex: "O autor descreve...", "O texto apresenta...").
2. Criar um título curto e representativo, com no máximo 31 caracteres.
3. Gerar três tags que NÃO estejam nesta lista: {taglist}.
4. Listar palavras-chave relevantes.

⚠️ Importante:
- Não use "eu", "nós" ou expressões em primeira pessoa.
- O campo "descricao" deve conter apenas o resumo em terceira pessoa.

Responda apenas em JSON, no formato:
{{
  "titulo": "Título curto (até 31 caracteres)",
  "descricao": "Resumo do conteúdo em terceira pessoa",
  "tag1": "Primeira tag",
  "tag2": "Segunda tag",
  "tag3": "Terceira tag",
  "palavras_chaves": ["x", "y", "z"]
}}
"""

# Prompt para correção de formato JSON
promptCorrecao = """
Sua resposta anterior não está em JSON válido.
Por favor, gere novamente no formato:
{
  "titulo": "...",
  "descricao": "...",
  "tag1": "...",
  "tag2": "...",
  "tag3": "...",
  "palavras_chaves": ["x", "y", "z"]
}
"""

# --------------------------
# 🔹 Funções auxiliares
# --------------------------

async def chamar_llama(prompt, max_tokens=180):
    """Requisição à API local do LLaMA"""
    timeout = aiohttp.ClientTimeout(total=600)  # 2 minutos
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            "model": LLAMA_MODEL,
            "prompt": prompt,
            "num_predict": max_tokens,
            "temperature": 0.3,
            "stream": False
        }
        async with session.post(LLAMA_API_URL, json=payload) as resp:
            data = await resp.json()
            return data.get("response", "").strip()

async def get_json_from_llama(prompt, max_tokens=180, tentativas=3):
    """Garante que a resposta venha em JSON válido"""
    for _ in range(tentativas):
        resposta = await chamar_llama(prompt, max_tokens)
        try:
            result = json.loads(resposta)
            # Garantir que o título não ultrapasse 31 caracteres
            if len(result.get("titulo", "")) > 31:
                result["titulo"] = result["titulo"][:31]
            return result
        except json.JSONDecodeError:
            print("⚠️ Resposta inválida, tentando novamente...")
            prompt = f"{promptCorrecao}\n\nResposta anterior:\n{resposta}"
    # Se falhar após tentativas
    return {
        "titulo": "Indefinido",
        "descricao": "Indefinido",
        "tag1": "Indefinido",
        "tag2": "Indefinido",
        "tag3": "Indefinido",
        "palavras_chaves": ["Indefinido"]
    }

# --------------------------
# 🔹 Funções principais
# --------------------------

async def iniciarConversa(str):
    """
    Recebe tokens do front-end e gera resumo, título, tags e palavras-chave.
    """
    prompt = f"{promptIntroducao}\n\nTokens do conteúdo: {str}\n\n" \
             "Use os tokens para gerar resumo, título, tags e palavras-chave em terceira pessoa."
    result = await get_json_from_llama(prompt, max_tokens=180)
    return result

async def classificarTagsGerais(descricao):
    """
    Classifica a descrição em **uma única tag da lista fornecida**.
    """
    prompt = f"""
Você receberá uma descrição e uma lista de tags principais.

Escolha apenas UMA tag da lista abaixo que mais se relacione ao conteúdo:
{taglist}

⚠️ Regras importantes:
- Retorne **somente uma palavra** presente nesta lista.
- Não adicione explicações, exemplos ou texto adicional.
- Se a descrição não se encaixar claramente, retorne "OUTROS".

Descrição do conteúdo:
{descricao}
"""

    resposta = await chamar_llama(prompt, max_tokens=20)
    resposta = resposta.strip().upper()  # Padroniza para maiúscula

    if resposta not in taglist:
        print(f"⚠️ Tag '{resposta}' não está na lista. Retornando 'OUTROS'.")
        resposta = "OUTROS"

    return resposta

all = ['iniciarConversa', 'classificarTagsGerais']