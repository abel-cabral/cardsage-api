import json
import os
import redis

from .mongodb import todos_cards


# Criar uma instância do cliente Redis
r = redis.Redis.from_url(os.getenv('REDIS_URL'))

def update_cache(user_id):
    # Atualiza o cache para a lista de itens
    items = todos_cards(user_id)
    r.set(user_id, items)

def add_item_to_cache(user_id, new_item):
    # Pega os dados atuais
    cached_data = r.get(user_id)
    
    if cached_data:
        # Decodifica e transforma em lista Python
        items = json.loads(cached_data.decode('utf-8'))
    else:
        items = []

    # Adiciona o novo item ao final da lista
    items.append(new_item)

    # Salva novamente no Redis
    r.set(user_id, json.dumps(items))