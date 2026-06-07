import re

from flask_jwt_extended import get_jwt_identity
from .mongodb import collection

def search_query(query):
    colecao = collection()
    user_id = get_jwt_identity()

    # Configuração da consulta de busca textual no Atlas Search
    search_query = {
        "$search": {
            "index": "card_sage",  # Nome do índice no Atlas Search
            "text": {
                "query": query,  # String de busca
                "path": ["_id", "cards.conteudo", "cards.palavras_chaves", "cards.descricao"]  # Campos onde a busca será realizada
            }
        }
    }

    # Definição da pipeline de agregação
    pipeline = [
        search_query,  # Etapa de busca textual
        {"$match": {"user_id": user_id}},  # Filtrar documentos pelo user_id
        {"$unwind": "$cards"},  # Desfazer arrays (se cards for um array)
        {"$addFields": {"score": {"$meta": "searchScore"}}},  # Adicionar campo de score
        {"$sort": {"score": -1}},  # Ordenar por score decrescente
        {"$facet": {
            "results": [
                {"$limit": 5},  # Limitar a 5 resultados
                {"$project": {
                    "_id": 0,
                    "cards.descricao": 1,
                    "cards.titulo": 1,
                    "cards._id": 1,
                    "score": 1
                }}
            ],
            "all_cards": [
                {"$project": {
                    "cards": 1,
                    "_id": 0
                }}
            ],
            "first_score": [
                {"$limit": 1},  # Limitar a 1 resultado para o primeiro score
                {"$project": {"score": {"$meta": "searchScore"}}}
            ]
        }}
    ]

    try:
        results = list(colecao.aggregate(pipeline))  # Executar a pipeline de agregação

        if not results or not results[0]["results"]:
            print("Nenhum resultado encontrado.")
            return []
        else:
            # Obter a pontuação do primeiro resultado encontrado
            first_score = results[0]["first_score"][0]["score"]

            # Valor do maior score
            max_score = max(result["score"] for result in results[0]["results"])
            
            # Se o maior score for menor que x, deve retornar vazio
            if max_score < 0.8:
                return []

            # Extrair todos os cards que correspondem à pesquisa
            all_cards = [result["cards"] for result in results[0]["all_cards"]]

            # Verificar se há resultados
            if not results[0]["results"]:
                print("Nenhum resultado encontrado.")
                return []
            else:
                return all_cards
                

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
        return []
    
def search_tags(tags_para_buscar):
    colecao = collection()
    user_id = get_jwt_identity()
    tags_lower = [t.lower() for t in tags_para_buscar]

    # Regex case-insensitive para cada tag em cada campo — compatível com dados antigos (caixa mista)
    or_conditions = [
        {f'cards.tag{i}': {'$regex': f'^{re.escape(tag)}$', '$options': 'i'}}
        for tag in tags_para_buscar
        for i in range(1, 4)
    ]

    cursor = colecao.find(
        {'user_id': user_id, '$or': or_conditions},
        {'cards.embedding': 0, 'cards.conteudo': 0, 'cards.palavras_chaves': 0}
    )

    resultados = []
    for doc in cursor:
        cards_match = [
            card for card in doc.get('cards', [])
            if any(card.get(f'tag{i}', '').lower() in tags_lower for i in range(1, 4))
        ]
        if cards_match:
            for card in cards_match:
                card['_id'] = str(card['_id'])
            resultados.append({'_id': str(doc['_id']), 'cards': cards_match})

    return resultados