import os
import redis

from .mongodb import todos_cards


# Criar uma instância do cliente Redis
r = redis.Redis.from_url(os.getenv('REDIS_URL'))

def update_cache(user_id):
    # Atualiza o cache para a lista de itens
    items = todos_cards(user_id)
    r.set(user_id, items)

