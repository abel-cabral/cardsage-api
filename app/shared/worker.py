import asyncio

from .chatgpt import iniciarConversa, classificarTagsGerais
from .mongodb import adicionar_card

async def processar_async(user_id, url, html_texto):
    """Processamento real da IA e salvamento"""
    chatData = await iniciarConversa(html_texto)
    tag = await classificarTagsGerais(chatData['descricao'])

    # Normaliza tags para minúsculo para garantir busca case-insensitive consistente
    for field in ('tag1', 'tag2', 'tag3'):
        if isinstance(chatData.get(field), str):
            chatData[field] = chatData[field].lower()

    chatData['url'] = url
    chatData['tag_raiz'] = tag
    chatData['conteudo'] = html_texto
    chatData['imageUrl'] = 'https://images.unsplash.com/photo-1557724630-96de91632c3b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2MTg2MTd8MHwxfHNlYXJjaHwxfHx1bmRlZmluZWR8ZW58MHwwfHx8MTcxNzg2MzEzMnww&ixlib=rb-4.0.3&q=80&w=1080'

    mongo_response = adicionar_card(chatData, user_id)

    if mongo_response.get('operacaoMongo') == 0:
        print("❌ Erro ao salvar no MongoDB.")
        return False

    print(f"✅ Item processado e salvo: {url}")
    return mongo_response


def processar_item(user_id, url, html_texto):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(processar_async(user_id, url, html_texto))
    finally:
        loop.close()
