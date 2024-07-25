import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Verificar se a variável TAGLIST está carregada corretamente
taglist = os.getenv('TAGLIST').split(',')

client = AsyncOpenAI(
    organization=os.getenv('ORGANIZATION'),
    project=os.getenv('PROJECT_ID'),
    api_key=os.getenv('OPENAI_API_KEY')
)

promptIntroducao = """
Você receberá um texto. Sua tarefa é:

1. Resumir o texto em até duas linhas (máximo de 200 caracteres).
2. Gerar três tags que não sejam nenhuma desta lista: {0}.
   - A soma dos caracteres das três tags (tag1, tag2, tag3) não pode ultrapassar 31 caracteres.
3. Gerar um título para o texto (máximo de 31 caracteres).
4. Listar todas as palavras-chave encontradas no texto.

A resposta deve ser unicamente no formato JSON com as seguintes propriedades:
- 'titulo': Título do resumo (máximo de 31 caracteres)
- 'descricao': Resumo do texto (máximo de 200 caracteres)
- 'palavras_chaves': Lista de palavras-chave
- 'tag1': Primeira tag
- 'tag2': Segunda tag
- 'tag3': Terceira tag

Obs: Se não houver informações suficientes, classifique todos os campos como 'Indefinido'.
Se o texto estiver em outro idioma, traduza 'titulo' e 'descricao' para pt-BR.

Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 31 caracteres)",
    "descricao": "Resumo do texto (máximo de 200 caracteres)",
    "tag1": "Primeira tag",
    "tag2": "Segunda tag",
    "tag3": "Terceira tag",
    "palavras_chaves": ["x", "y", "z"]
}}
""".format(taglist)

promptClassificarTag = """
Você receberá um array contendo 20 tags raízes e um texto.
Sua tarefa é:

1. Retornar o nome da tag raiz que mais se relaciona com o texto.
2. Listar todas as palavras-chave encontradas no texto.

A tag gerada deve ser necessariamente uma das seguintes tags: {0}.
Se o texto parecer estranho ou sem sentido, possivelmente devido a um erro de extração, retorne 'Indefinido'.

Formato esperado:
Uma única palavra, que é o nome da tag raiz mais relevante.
""".format(taglist)

promptCorrecao = """
Sua resposta anterior não atendeu aos requisitos. Por favor, forneça uma nova resposta que atenda aos seguintes requisitos:

1. 'titulo': Título do resumo (máximo de 31 caracteres, jamais deve superar isso).
2. 'descricao': Resumo do texto (máximo de 200 caracteres).
3. 'tag1', 'tag2', 'tag3': A soma dos caracteres das três tags não pode ultrapassar 31 caracteres.
4. 'palavras_chaves': Lista de palavras-chave.

Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 31 caracteres)",
    "descricao": "Resumo do texto (máximo de 200 caracteres)",
    "tag1": "Primeira tag",
    "tag2": "Segunda tag",
    "tag3": "Terceira tag",
    "palavras_chaves": ["x", "y", "z"]
}}
"""

async def get_chatgpt_response(messages):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )
    return response

async def validar_resposta(chat, vezes=0):
    try:
        content = chat.choices[0].message.content
        result = json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        if vezes < 3:
            return await validar_resposta(response, vezes + 1)
        raise ValueError("Resposta do OpenAI API não está no formato esperado: {}".format(str(e)))

    needs_correction = False
    correction_instructions = []

    if len(result["titulo"]) > 31:
        needs_correction = True
        correction_instructions.append("Não esta certo, tente de outra forma! O campo 'titulo' excedeu 31 caracteres.")
    if len(result["descricao"]) > 200:
        needs_correction = True
        correction_instructions.append("Não esta certo, tente de outra forma! O campo 'descricao' excedeu 200 caracteres.")
    if len(result["tag1"]) + len(result["tag2"]) + len(result["tag3"]) > 31:
        needs_correction = True
        correction_instructions.append("Não esta certo, tente de outra forma! A soma das tags 'tag1', 'tag2' e 'tag3' excedeu o total máximo permitido de 31 caracteres. Gere novas tags menores.")

    if needs_correction:
        correction_message = "\n".join(correction_instructions)
        messages = [
            {"role": "system", "content": promptCorrecao},
            {"role": "assistant", "content": content},
            {"role": "user", "content": correction_message}
        ]
        response = await get_chatgpt_response(messages)
        if vezes < 5:
            return await validar_resposta(response, vezes + 1)
    return chat

async def iniciarConversa(htmlText):
    messages = [{"role": "system", "content": promptIntroducao}, {"role": "user", "content": htmlText}]
    response = await get_chatgpt_response(messages)
    result = await validar_resposta(response)
    return result.choices[0].message.content

async def classificarTagsGerais(descricao):
    obj = {
        "tagsRaizes": taglist,
        "descricao": descricao
    }

    message = [
        {"role": "system", "content": promptClassificarTag},
        {"role": "user", "content": json.dumps(obj)}
    ]
    response = await get_chatgpt_response(message)
    result = await validar_tag(response)
    return result.choices[0].message.content

async def validar_tag(chat, vezes=0):
    try:
        content = chat.choices[0].message.content
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise ValueError("Resposta do OpenAI API não está no formato esperado: {}".format(str(e)))

    needs_correction = False
    correction_instructions = []

    if content not in taglist:
        needs_correction = True
        correction_instructions.append("Não esta certo, tente de outra forma! A tag_raiz informada não está presente na lista informada {}. A tag_raiz deve ser uma tag presente nesta lista.".format(taglist))

    if needs_correction:
        correction_message = "\n".join(correction_instructions)
        messages = [
            {"role": "system", "content": promptClassificarTag},
            {"role": "assistant", "content": content},
            {"role": "user", "content": correction_message}
        ]
        response = await get_chatgpt_response(messages)
        if vezes < 5:
            return await validar_tag(response, vezes + 1)
    return chat

all = ['iniciarConversa', 'classificarTagsGerais']