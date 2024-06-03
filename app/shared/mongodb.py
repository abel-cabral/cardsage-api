import os
import json
import uuid

from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

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

# Função para adicionar um novo ramo à tag raiz ou cria-la
def adicionar_ramo(tag_raiz, novo_ramo):
    # Obter a coleção
    db = collection()

    # Verificar se já existe um ramo com a mesma URL
    documento = db.find_one({"tag_raiz": tag_raiz, "ramos.url": novo_ramo["url"]})
    if documento:
        return {"message": "Um ramo com essa URL já existe."}

    # Gerar um ID único para o novo ramo
    novo_ramo["_id"] = str(uuid.uuid4())

    # Adicionar o novo ramo ao array de ramos no documento da tag raiz
    resultado = db.update_one(
        {"tag_raiz": tag_raiz},
        {"$push": {"ramos": novo_ramo}},
        upsert=True
    )

    # Buscar novamente o documento atualizado
    documento_atualizado = db.find_one({"tag_raiz": tag_raiz})
    documento_atualizado['_id'] = str(documento_atualizado['_id'])

    return documento_atualizado

def todos_ramos():
    # Obter a coleção
    db = collection()

    # Recuperar todos os documentos com base no critério
    documentos = db.find()
    
    # Converter os documentos em uma lista para facilitar o manuseio
    lista_documentos = list(documentos)

    # Converter ObjectId para strings
    for doc in lista_documentos:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])

    # Serializar a lista de documentos para JSON
    json_documentos = json.dumps(lista_documentos)

    return json_documentos

def deletar_ramo_por_id(ramo_id):
    # Obter a coleção
    db = collection()

    # Atualizar o documento para remover o ramo com o ID especificado
    resultado = db.update_one(
        {"ramos._id": ramo_id},
        {"$pull": {"ramos": {"_id": ramo_id}}}
    )

    # Verificar se o ramo foi deletado com sucesso
    if resultado.modified_count == 1:
        return f"Ramo com ID {ramo_id} deletado com sucesso."
    else:
        return f"Nenhum ramo encontrado com o ID {ramo_id}."

# Apenas 'collection' será exportado quando importado de outro script
__all__ = ['collection', 'adicionar_ramo', 'todos_ramos', 'deletar_ramo_por_id']