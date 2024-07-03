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
Resuma o texto em até duas linhas (máximo 200 caracteres).
Com base no texto, gere três tags que não seja nenhum desta lista: {}, cuja a soma dos caracteres das três tags (tag1, tag2 e tag3), não pode ultrapasse o total de 31 caracteres.
Gere um título (máximo de 31 caracteres) para o texto. Uma propriedade chamada de 'palavras_chaves' ela deve ser uma lista com todas as palavras chaves encontradas.
A resposta deve ser unicamente no formato JSON com as seguintes propriedades:
- 'titulo' (título do resumo, máximo de 31 caracteres)
- 'descricao' (resumo, máximo de 200 caracteres)
- 'palavras_chaves': []
- 'tag1'
- 'tag2'
- 'tag3'

Obs1. 

Obs2. Se não houver informações suficientes, classifique todos os campos como 'Indefinido'.
'titulo' e 'descricao' devem ser traduzidos para pt-BR caso a página seja em outro idioma.

Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 31 caracteres)",
    "descricao": "Resumo do texto (máximo de 200 caracteres)",
    "tag1": "Primeira",
    "tag2": "Segunda",
    "tag3": "Terceira",
    "palavras_chaves": ["x", "y", "z"]
    
}}
""".format(taglist)

promptClassificarTag = """
Você receberá um array contendo 20 tags raízes e um texto.
Retorne o nome da tag raiz que mais se relaciona com o texto.
A tag gerada deve ser necessariamente uma das seguintes tags: [{}].
palavras_chaves deve ter todas as palavras chaves relacionadas com o texto.
Se o texto parecer estranho ou sem sentido, possivelmente devido a um erro de extração, retorne 'Indefinido'.

Formato da resposta esperada: uma única palavra, que é o nome da tag raiz mais relevante.
""".format(taglist)

promptCorrecao = """
Por favor, forneça uma nova resposta que atenda aos requisitos.
Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 31 caracteres, jamais deve superar isso)",
    "descricao": "Resumo do texto (máximo de 200 caracteres)",
    "tag1": "Primeira",
    "tag2": "Segunda",
    "tag3": "Terceira",
    "palavras_chaves": ["x", "y", "z"]
}}
"""

async def get_chatgpt_response(messages):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        temperature=0.2
    )
    return response

async def validar_resposta(chat, vezes=0):
    try:
        content = chat.choices[0].message.content
        result = json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise ValueError("Resposta do OpenIA API não está no formato esperado: {}".format(str(e)))

    needs_correction = False
    correction_instructions = []

    if len(result["titulo"]) > 31:
        needs_correction = True
        correction_instructions.append("titulo excedeu 31 caracteres.")
    if len(result["descricao"]) > 200:
        needs_correction = True
        correction_instructions.append("descricao excedeu 200 caracteres.")
    if len(result["palavras_chaves"]) <= 0:
        needs_correction = True
        correction_instructions.append("Nenhuma palavra chave encontrada.")
    if len(result["tag1"]) + len(result["tag2"]) + len(result["tag3"]) >= 31:
        needs_correction = True
        correction_instructions.append("A soma das tags 1, 2 e 3 excedeu o total máximo permitido de até 31 caracteres. Gere novas tags menores")

    if needs_correction:
        correction_message = "\n".join(correction_instructions)
        messages = [
            {"role": "system", "content": promptCorrecao},
            {"role": "assistant", "content": content},
            {"role": "user", "content": correction_message}
        ]
        response = await get_chatgpt_response(messages)
        if vezes < 5:
            return await validar_resposta(response , vezes + 1)
        else:
            raise ValueError("Falha ao corrigir a resposta após 3 tentativas.")
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
        raise ValueError("Resposta do OpenIA API não está no formato esperado: {}".format(str(e)))

    needs_correction = False
    correction_instructions = []

    if content not in taglist:
        needs_correction = True
        correction_instructions.append("A tag_raiz informada não está presente na lista informada {}, tag_raiz deve ser uma tag presente nesta lista".format(taglist))

    if needs_correction:
        correction_message = "\n".join(correction_instructions)
        messages = [
            {"role": "system", "content": promptClassificarTag},
            {"role": "assistant", "content": content},
            {"role": "user", "content": correction_message}
        ]
        response = await get_chatgpt_response(messages)
        if vezes < 3:
            return await validar_tag(response , vezes + 1)
        else:
            raise ValueError("Falha ao corrigir a resposta após 3 tentativas.")
    return chat

all = ['iniciarConversa', 'classificarTagsGerais']