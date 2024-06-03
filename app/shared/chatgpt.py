import os
import json

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
  organization=os.getenv('ORGANIZATION'),
  project=os.getenv('PROJECT_ID'),
  api_key=os.getenv('OPENAI_API_KEY')
)

instrucao = "Resuma o texto em até duas linhas (máximo 240 caracteres); Gere três tags de uma palavra que não sejam [{}], e que representem os principais tópicos do texto; Gere um titulo para o texto; A resposta deve ser unicamente no formato JSON com as seguintes propriedades: titulo (titulo do resumo), descricao (resumo), tag1 (primeira tag), tag2 (segunda tag) e tag3 (terceira tag); Se não ouver informações o suficiente classifique como 'Indefinido' em todos os campos".format(os.getenv('TAGLIST'))

async def get_chatgpt_response(messages):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3
    )
    return response

async def enviar_partes(partes):
    messages = []
    messages.append({"role": "system", "content": "Será enviado {} parte/s, não responda nada, apenas aguarde receber todas, em seguinda será enviado um novo prompt.".format(len(partes))})
    
    for i, parte in enumerate(partes):
        messages.append({"role": "user", "content": parte})
        response = await get_chatgpt_response(messages)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
    messages.append({"role": "system", "content": "Com base nas partes recebidas: {}".format(instrucao)})
    response = await get_chatgpt_response(messages)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return messages

async def iniciarConversa(htmlText):
    messages = [{"role": "system", "content": instrucao}, {"role": "user", "content": htmlText}]
    response = await get_chatgpt_response(messages)
    return response

async def classificarTagsGerais(raizes, descricao):
    obj = {
        "tagsRaizes": raizes,
        "descricao": descricao
    }
    message = [
        {"role": "system", "content": ("A Resposta deverá ser uma unica palavra; Irá receber dois elementos: o primeiro array contém 20 tags raízes e o segundo contém um texto; Retorne somente com apenas somente 1 palavra o nome da tag raiz que mais tem haver com texto. ex: 'Games'")},
        {"role": "user", "content": json.dumps(obj)}
    ]
    return await get_chatgpt_response(message)

__all__ = ['iniciarConversa', 'classificarTagsGerais']