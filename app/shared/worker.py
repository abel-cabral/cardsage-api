import asyncio

from .chatgpt import iniciarConversa, classificarTagsGerais
from .mongodb import adicionar_card
from .util import partirHTML

async def processar_async(user_id, url, html_texto):
    """Processamento real da IA e salvamento. Retorna (sucesso, dados).

    `dados` é sempre o `chatData` montado até onde o processamento avançou —
    mesmo em caso de falha — para que possa ser registrado pelo worker da fila.
    """
    chatData = {'url': url, 'conteudo': html_texto}
    try:
        # qwen2.5:3b via rkllama tem contexto de 2048 tokens — trunca antes de enviar
        chatData.update(await iniciarConversa(partirHTML(html_texto, max_length=4000)[0]))
        tag = await classificarTagsGerais(chatData['descricao'])

        # Normaliza tags para minúsculo para garantir busca case-insensitive consistente
        for field in ('tag1', 'tag2', 'tag3'):
            if isinstance(chatData.get(field), str):
                chatData[field] = chatData[field].lower()

        chatData['tag_raiz'] = tag
        chatData['imageUrl'] = 'https://images.unsplash.com/photo-1557724630-96de91632c3b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2MTg2MTd8MHwxfHNlYXJjaHwxfHx1bmRlZmluZWR8ZW58MHwwfHx8MTcxNzg2MzEzMnww&ixlib=rb-4.0.3&q=80&w=1080'

        mongo_response = adicionar_card(chatData, user_id)

        if mongo_response.get('operacaoMongo') == 0:
            print("❌ Erro ao salvar no MongoDB.")
            return False, chatData

        print(f"✅ Item processado e salvo: {url}")
        return True, mongo_response
    except Exception as e:
        print(f"❌ Erro ao processar item ({url}): {e}")
        return False, chatData


def processar_item(user_id, url, html_texto):
    """Roda o processamento assíncrono e retorna (sucesso, dados)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(processar_async(user_id, url, html_texto))
    finally:
        loop.close()
