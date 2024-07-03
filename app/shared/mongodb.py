import os
import json
import uuid

from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity

load_dotenv()

client = MongoClient(os.getenv('DBHOST'), 27017)
# Substitua 'mydatabase' pelo nome do seu banco de dados MongoDB
db = client[os.getenv('DATABASE')]
# Substitua 'mycollection' pelo nome da sua coleção MongoDB
collection = db[os.getenv('COLLECTION')]

def collection(collection=False):
    if (collection):
        return db[collection]
    return db[os.getenv('COLLECTION')]

# Função para adicionar um novo card à tag raiz ou cria-la
def adicionar_card(novo_card):
    # Obter a coleção
    db = collection()
    user_id = get_jwt_identity()

    # Gerar um ID único para o novo card
    novo_card["_id"] = str(uuid.uuid4())

    # Adicionar o novo card ao array de cards no documento da tag raiz
    novo_card['operacaoMongo'] = db.update_one(
        {"user_id": user_id},
        {"$push": {"cards": novo_card}},
        upsert=True
    )

    return novo_card

# Função para atualizar card adicionando url
def atualizar_card(card_id, imageUrl, user_id):
    # Obter a coleção
    db = collection()

    # Atualizar o campo imageUrl do card específico no array cards
    resultado = db.update_one(
        {"user_id": user_id, "cards._id": card_id},
        {"$set": {"cards.$.imageUrl": imageUrl}},
        upsert=True  # Isso permite criar o campo se ele não existir
    )

    return resultado


def todos_cards():
     # Obter o ID do usuário atual
    user_id = get_jwt_identity()

    # Recuperar todos os documentos associados ao ID do usuário
    documentos = collection().find(
        {"user_id": user_id},
        {"cards.palavras_chaves": 0, "cards.conteudo": 0}
    )

    # Converter os documentos em uma lista para facilitar o manuseio
    lista_documentos = list(documentos)

    # Inverter a lista de cards em cada documento
    for doc in lista_documentos:
        if 'cards' in doc:
            doc['cards'] = list(reversed(doc['cards']))

    # Converter ObjectId para strings
    for doc in lista_documentos:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        if 'cards' in doc:
            for card in doc['cards']:
                if '_id' in card:
                    card['_id'] = str(card['_id'])

    # Serializar a lista de documentos para JSON
    json_documentos = json.dumps(lista_documentos)
    
    return json_documentos

def deletar_card_por_id(user_id, card_id):
    # Obter a coleção
    db = collection()

    # Atualizar o documento para remover o card com o ID especificado
    resultado = db.update_one(
        {"user_id": user_id},
        {"$pull": {"cards": {"_id": card_id}}}
    )

    # Verificar se o card foi deletado com sucesso
    if resultado.modified_count > 0:
        return f"Ramo com ID {card_id} deletado com sucesso."
    else:
        return f"Nenhum card encontrado com o ID {card_id}."

# Apenas 'collection' será exportado quando importado de outro script
__all__ = ['collection', 'adicionar_card', 'todos_cards', 'deletar_card_por_id', 'atualizar_card']