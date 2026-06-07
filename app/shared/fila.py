import json
import os

import redis

from .cache_utils import update_cache
from .worker import processar_item

FILA_KEY = 'fila_itens'
LOG_ERRO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs_error.txt')

r = redis.Redis.from_url(os.getenv('REDIS_URL'))


def enfileirar_item(user_id, url, html_texto):
    """Adiciona um item ao final da fila de processamento."""
    item = {'user_id': user_id, 'url': url, 'html_texto': html_texto, 'ciclo': 1}
    r.lpush(FILA_KEY, json.dumps(item))


def _registrar_falha(chat_data):
    with open(LOG_ERRO_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(chat_data, ensure_ascii=False) + '\n')


def processar_fila():
    """Consome a fila um item por vez (processo dedicado, fora do gunicorn).

    Cada item recebe até 2 ciclos de 2 tentativas: se falhar 2x, volta para o
    final da fila (ciclo 2); se falhar mais 2x, é descartado e o `chatData`
    é registrado em `logs_error.txt`.
    """
    print("👷 Worker da fila iniciado, aguardando itens...")
    while True:
        _, bruto = r.brpop(FILA_KEY)
        item = json.loads(bruto)
        user_id, url, html_texto = item['user_id'], item['url'], item['html_texto']
        ciclo = item.get('ciclo', 1)

        sucesso, dados = processar_item(user_id, url, html_texto)
        if not sucesso:
            sucesso, dados = processar_item(user_id, url, html_texto)

        if sucesso:
            update_cache(user_id)
            continue

        if ciclo == 1:
            print(f"↩️  '{url}' falhou 2x — voltando para o final da fila (ciclo 2)")
            item['ciclo'] = 2
            r.lpush(FILA_KEY, json.dumps(item))
        else:
            print(f"🗑️  '{url}' falhou novamente — descartando e registrando em logs_error.txt")
            _registrar_falha(dados)


__all__ = ['enfileirar_item', 'processar_fila']
