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

instrucao = "Texto extraído de uma página HTML usando `document.body.innerText`, faça um resumo em até duas linhas (máximo 160 caracteres) e forneça três tags que representem os principais tópicos do texto. A resposta deve ser unicamente no formato JSON com as seguintes propriedades: mensagem (resumo), tag1 (primeira tag), tag2 (segunda tag) e tag3 (terceira tag), sem mais nenhum texto adicional."

async def get_chatgpt_response(messages):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    return response

async def enviar_partes(partes):
    messages = []
    messages.append({"role": "system", "content": "Será enviado {} parte/s, não responda nada, apenas aguarde receber todas, em seguinda será enviado um novo prompt.".format(len(partes))})
    
    for i, parte in enumerate(partes):
        messages.append({"role": "user", "content": parte})
        response = await get_chatgpt_response(messages)
        print('{} --> {}'.format(i, messages))
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
    messages.append({"role": "system", "content": "Com base nas partes recebidas: {}".format(instrucao)})
    response = await get_chatgpt_response(messages)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    print('FIM --> {}'.format(response.choices[0].message.content))
    return messages

async def iniciarConversa(htmlText):
    messages = [{"role": "system", "content": instrucao}, {"role": "user", "content": htmlText}]
    response = await get_chatgpt_response(messages)
    return response

async def classificarTagsGerais(tagsRaizes, tags):
    message = [
        {"role": "system", "content": (
            "Você receberá dois arrays em formato de string: o primeiro array contém 20 tags principais (tags raízes) "
            "e o segundo array contém 3 tags secundárias (tags ramos). Sua tarefa é analisar as 3 tags secundárias e "
            "determinar qual das 20 tags principais está mais relacionada a essas tags secundárias. Retorne apenas o "
            "valor da tag principal (raiz) como uma string. Por exemplo, se as tags principais incluem 'games', 'cultura', "
            "'teatro', 'filmes', etc., e as tags secundárias são 'PS4', 'Assassin's Creed' e 'Ubisoft', a tag principal "
            "relacionada seria 'games'.")},
        {"role": "user", "content": f'{{"tags_raizes": {json.dumps(tagsRaizes)}, "tags_ramos": {json.dumps(tags)}}}'}
    ]
    response = await get_chatgpt_response(message)
    return response['choices'][0]['message']['content']

__all__ = ['iniciarConversa', 'classificarTagsGerais']