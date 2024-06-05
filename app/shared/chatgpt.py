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

instrucao = "Resuma o texto em até duas linhas (máximo 240 caracteres); Com base no texto, gere três tags de até 15 caracteres cada, não pode ser maior que esse tamanho, que não estejam nesta lista: [{}]; Gere um título para o texto. A resposta deve ser unicamente no formato JSON com as seguintes propriedades: 'titulo' (título do resumo), 'descricao' (resumo), 'tag1' (primeira tag), 'tag2' (segunda tag), e 'tag3' (terceira tag). Se não houver informações suficientes, classifique todos os campos como 'Indefinido'; titulo e descricao devem ser traduzidos para ptbr caso a pagina seja em outro idioma.".format(os.getenv('TAGLIST'))

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
        {"role": "system", "content": "A resposta deve ser uma única palavra. Você receberá dois elementos: um array contendo 20 tags raízes [{}] e um texto. Retorne o nome da tag raiz que mais se relaciona com o texto. Por exemplo: 'Games'. A tag gerada deve ser necessariamente uma das 20 tags do array fornecido. Se o texto parecer estranho ou sem sentido, possivelmente devido a um erro de extração, retorne 'Indefinido'.".format(os.getenv('TAGLIST'))},
        {"role": "user", "content": json.dumps(obj)}
    ]
    return await get_chatgpt_response(message)

__all__ = ['iniciarConversa', 'classificarTagsGerais']