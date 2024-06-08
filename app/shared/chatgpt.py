import os
import json

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Verificar se a variável TAGLIST está carregada corretamente
taglistEnv = os.getenv('TAGLIST')
taglist = taglistEnv.split(',')

client = AsyncOpenAI(
    organization=os.getenv('ORGANIZATION'),
    project=os.getenv('PROJECT_ID'),
    api_key=os.getenv('OPENAI_API_KEY')
)

promptIntroducao = """
Resuma o texto em até duas linhas (máximo 210 caracteres).
Com base no texto, gere três tags de no MÁXIMO 17 caracteres (jamais maior do que isto) e que não seja nenhum desta lista: {}.
Gere um título (máximo de 32 caracteres) para o texto.
A resposta deve ser unicamente no formato JSON com as seguintes propriedades:
- 'titulo' (título do resumo, máximo de 32 caracteres)
- 'descricao' (resumo, máximo de 210 caracteres)
- 'tag1' (primeira tag, máximo de 17 caracteres)
- 'tag2' (segunda tag, máximo de 17 caracteres)
- 'tag3' (terceira tag, máximo de 17 caracteres)

Se não houver informações suficientes, classifique todos os campos como 'Indefinido'.
'titulo' e 'descricao' devem ser traduzidos para pt-BR caso a página seja em outro idioma.

Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 32 caracteres)",
    "descricao": "Resumo do texto (máximo de 210 caracteres)",
    "tag1": "Primeira tag (máximo de 17 caracteres)",
    "tag2": "Segunda tag (máximo de 17 caracteres)",
    "tag3": "Terceira tag (máximo de 17 caracteres)"
}}
""".format(taglist)

promptClassificarTag = """
Você receberá um array contendo 20 tags raízes e um texto.
Retorne o nome da tag raiz que mais se relaciona com o texto.
A tag gerada deve ser necessariamente uma das 20 tags do array fornecido.
Se o texto parecer estranho ou sem sentido, possivelmente devido a um erro de extração, retorne 'Indefinido'.

Formato da resposta esperada: uma única palavra, que é o nome da tag raiz mais relevante.

Exemplo de entrada:
{{
"tagsRaizes": {},
"descricao": "Texto de exemplo para análise"
}}

Exemplo de saída:
"Desenvolvimento "
""".format(taglist)

promptCorrecao = """
Por favor, forneça uma nova resposta que atenda aos requisitos.
Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 32 caracteres, jamais deve superar isso)",
    "descricao": "Resumo do texto (máximo de 210 caracteres)",
    "tag1": "Primeira tag (máximo de 17 caracteres)",
    "tag2": "Segunda tag (máximo de 17 caracteres)",
    "tag3": "Terceira tag (máximo de 17 caracteres)"
}}
"""

async def get_chatgpt_response(messages):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1
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

    if len(result["titulo"]) > 32:
        needs_correction = True
        correction_instructions.append("titulo excedeu 12 caracteres.")
    if len(result["descricao"]) > 210:
        needs_correction = True
        correction_instructions.append("descricao excedeu 210 caracteres.")
    if len(result["tag1"]) > 17:
        needs_correction = True
        correction_instructions.append("tag1 excedeu 15 caracteres.")
    if len(result["tag2"]) > 17:
        needs_correction = True
        correction_instructions.append("tag2 gerada excedeu 15 caracteres.")
    if len(result["tag3"]) > 17:
        needs_correction = True
        correction_instructions.append("tag3 gerada excedeu 15 caracteres.")

    if needs_correction:
        correction_message = "\n".join(correction_instructions)
        messages = [
            {"role": "system", "content": promptCorrecao},
            {"role": "assistant", "content": content},
            {"role": "user", "content": correction_message}
        ]
        response = await get_chatgpt_response(messages)
        if vezes < 3:
            return await validar_resposta(response , vezes + 1)
        else:
            raise ValueError("Falha ao corrigir a resposta após 3 tentativas.")
    return result

async def iniciarConversa(htmlText):
    messages = [{"role": "system", "content": promptIntroducao}, {"role": "user", "content": htmlText}]
    response = await get_chatgpt_response(messages)
    result = await validar_resposta(response)
    return result

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
    return result

async def validar_tag(chat, vezes=0):
    try:
        value = chat.choices[0].message.content
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise ValueError("Resposta do OpenIA API não está no formato esperado: {}".format(str(e)))

    needs_correction = False
    correction_instructions = []

    if value not in taglist:
        needs_correction = True
        correction_instructions.append("A tag_raiz informada não está presente na lista informada {}, tag_raiz deve ser uma tag presente nesta lista".format(taglist))

    if needs_correction:
        print(taglist)
        print(chat)
        correction_message = "\n".join(correction_instructions)
        messages = [
            {"role": "system", "content": promptClassificarTag},
            {"role": "assistant", "content": value},
            {"role": "user", "content": correction_message}
        ]
        response = await get_chatgpt_response(messages)
        if vezes < 3:
            return await validar_tag(response , vezes + 1)
        else:
            raise ValueError("Falha ao corrigir a resposta após 3 tentativas.")
    return value

all = ['iniciarConversa', 'classificarTagsGerais']