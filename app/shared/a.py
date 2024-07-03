from mongodb import collection
#from flask_jwt_extended import get_jwt_identity


colecao = collection()
#user_id = get_jwt_identity()

# Definir o user_id e a consulta de pesquisa
# Definir o user_id e a consulta de pesquisa
user_id = "6663787faf3192e514b3b2c7"
query = "Cursos e certificações"
search_query = {
    "$search": {
        "index": "busca_usando_linguagem_natural",
        "text": {
            "query": query,
            "path": {"wildcard": "*"}
        }
    }
}

pipeline = [
    search_query,
    {"$match": {"user_id": user_id}},
    {"$unwind": "$cards"},
    {"$addFields": {"score": {"$meta": "searchScore"}}},
    {"$sort": {"score": -1}},
    {"$facet": {
        "results": [
            {"$project": {
                "_id": 0,
                "cards.descricao": 1,
                "cards.titulo": 1,
                "cards._id": 1,
                "score": 1
            }},
            {"$match": {"score": {"$gte": 0.1}}}  # Ajuste o limite conforme necessário
        ],
        "first_score": [
            {"$limit": 1},
            {"$project": {"score": {"$meta": "searchScore"}}}
        ]
    }}
]

try:
    results = list(colecao.aggregate(pipeline))

    if not results:
        print("Nenhum resultado encontrado.")
    else:
        # Obter a pontuação do primeiro resultado encontrado
        first_score = results[0]["first_score"][0]["score"]

        # Calcular a diferença de pontuação a partir do primeiro resultado
        max_score = max(result["score"] for result in results[0]["results"])
        score_diff = max_score - first_score

        # Definir um limite para a discrepância entre a pontuação máxima e a pontuação do primeiro resultado
        limite_discrepancia = 0.1  # Ajuste conforme necessário

        if score_diff > limite_discrepancia:
            print("Discrepância entre os scores é muito grande. Parando a pesquisa.")
        else:
            # Exibir as descrições e títulos dos cards mais relevantes
            for result in results[0]["results"]:
                print(f"Id: {result['cards']['_id']}")
                print(f"Título: {result['cards']['titulo']}")
                print(f"Descrição: {result['cards']['descricao']}")
                print(f"Score: {result['score']}\n")

            # Verificar se há resultados
            if not results[0]["results"]:
                print("Nenhum resultado encontrado.")

except Exception as e:
    print(f"Erro ao executar a consulta: {e}")