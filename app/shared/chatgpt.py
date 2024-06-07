import os
import json

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Verificar se a variável TAGLIST está carregada corretamente
taglist = os.getenv('TAGLIST')

client = AsyncOpenAI(
    organization=os.getenv('ORGANIZATION'),
    project=os.getenv('PROJECT_ID'),
    api_key=os.getenv('OPENAI_API_KEY')
)

promptIntroducao = """
Resuma o texto em até duas linhas (máximo 210 caracteres).
Com base no texto, gere três tags de no MÁXIMO 15 caracteres (jamais maior do que isto) e que não seja nenhum desta lista: {}.
Gere um título (máximo de 32 caracteres) para o texto.
A resposta deve ser unicamente no formato JSON com as seguintes propriedades:
- 'titulo' (título do resumo, máximo de 35 caracteres)
- 'descricao' (resumo, máximo de 210 caracteres)
- 'tag1' (primeira tag, máximo de 17 caracteres)
- 'tag2' (segunda tag, máximo de 17 caracteres)
- 'tag3' (terceira tag, máximo de 17 caracteres)

Se não houver informações suficientes, classifique todos os campos como 'Indefinido'.
'titulo' e 'descricao' devem ser traduzidos para pt-BR caso a página seja em outro idioma.

Formato esperado:
{{
    "titulo": "Título do resumo (máximo de 35 caracteres)",
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

async def get_chatgpt_response(messages):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3
    )
    return response

async def validar_resposta(response):
    try:
        content = response.choices[0].message.content
        result = json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise ValueError("Resposta da API não está no formato esperado: {}".format(str(e)))

    needs_correction = False
    correction_instructions = []

    if len(result["titulo"]) > 32:
        needs_correction = True
        correction_instructions.append("O título gerado excedeu 32 caracteres.")
    if len(result["descricao"]) > 210:
        needs_correction = True
        correction_instructions.append("A descrição gerada excedeu 210 caracteres.")
    if len(result["tag1"]) > 15:
        needs_correction = True
        correction_instructions.append("A primeira tag gerada excedeu 15 caracteres.")
    if len(result["tag2"]) > 15:
        needs_correction = True
        correction_instructions.append("A segunda tag gerada excedeu 15 caracteres.")
    if len(result["tag3"]) > 15:
        needs_correction = True
        correction_instructions.append("A terceira tag gerada excedeu 15 caracteres.")

    if needs_correction:
        correction_instruction = promptCorrecao
        messages = [
            {"role": "system", "content": promptIntroducao},
            {"role": "assistant", "content": response['choices'][0]['message']['content']},
            {"role": "user", "content": correction_instruction}
        ]
        response = await get_chatgpt_response(messages)
        result = response

    print(result)
    return result

async def enviar_partes(partes):
    messages = []
    messages.append({"role": "system", "content": "Será enviado {} parte/s, não responda nada, apenas aguarde receber todas, em seguida será enviado um novo prompt.".format(len(partes))})
    
    for i, parte in enumerate(partes):
        messages.append({"role": "user", "content": parte})
        response = await get_chatgpt_response(messages)
        messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            
    messages.append({"role": "system", "content": "Com base nas partes recebidas: {}".format(promptIntroducao)})
    response = await get_chatgpt_response(messages)
    result = await validar_resposta(response)
    messages.append({"role": "assistant", "content": json.dumps(result)})
    return messages

async def iniciarConversa(htmlText):
    messages = [{"role": "system", "content": promptIntroducao}, {"role": "user", "content": htmlText}]
    response = await get_chatgpt_response(messages)
    #result = await validar_resposta(response)
    return response

async def classificarTagsGerais(raizes, descricao):
    obj = {
        "tagsRaizes": raizes,
        "descricao": descricao
    }
    message = [
        {"role": "system", "content": promptClassificarTag},
        {"role": "user", "content": json.dumps(obj)}
    ]
    return await get_chatgpt_response(message)

all = ['iniciarConversa', 'classificarTagsGerais']