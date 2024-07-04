
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId
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
    
    tags_lower = [tag.lower() for tag in tags_para_buscar]

    # Construir a query para buscar documentos
    query = {
        '$or': [
            {'cards.tag1': {'$in': tags_lower}},
            {'cards.tag2': {'$in': tags_lower}},
            {'cards.tag3': {'$in': tags_lower}}
        ]
    }

    # Executar a query e obter os resultados
    cursor = colecao.find(query)
    print(cursor)

    # Lista para armazenar os resultados finais
    resultados = []

    # Iterar sobre os documentos retornados
    for doc in cursor:
        print(doc)
        # Verificar se pelo menos uma das tags está presente nos campos de tags do documento
        if any(tag.lower() in tags_lower for tag in doc['cards'].values() if isinstance(tag, str)):
            resultados.append({
                '_id': str(doc['_id']),
                'cards': doc['cards']
            })

    return resultados