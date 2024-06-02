import os
import json

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
def adicionar_ramo(tag_raiz, novo_ramo, url):
    # Obter a coleção
    db = collection()
    
    # Procurar o documento da tag raiz
    documento = db.find_one({"tag_raiz": tag_raiz})
    
    if documento:
        # A tag raiz existe, adicionar o novo ramo ao array de ramos
        response = db.update_one({"_id": documento["_id"]}, {"$push": {"ramos": novo_ramo}})
        # Retornar o documento atualizado convertendo o ID em string
        documento['_id'] = str(documento['_id'])
        return documento
    else:
        # A tag raiz não existe, criar um novo documento com a tag raiz e o novo ramo
        novo_documento = {
            "tag_raiz": tag_raiz,
            "ramos": [novo_ramo],
            "url": url
        }
        # Inserir o novo documento
        db.insert_one(novo_documento)
        # Retornar o documento inserido convertendo o ID em string
        novo_documento['_id'] = str(novo_documento['_id'])
        return novo_documento

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

def deletar_ramo_por_id(id):
    # Converter o ID para o tipo ObjectId
    obj_id = ObjectId(id)

    # Obter a coleção
    db = collection()

    # Deletar o documento com o ID especificado
    resultado = db.delete_one({"_id": obj_id})

    # Verificar se o documento foi deletado com sucesso
    if resultado.deleted_count == 1:
        return f"Documento com ID {id} deletado com sucesso."
    else:
        return f"Nenhum documento encontrado com o ID {id}."

# Apenas 'collection' será exportado quando importado de outro script
__all__ = ['collection', 'adicionar_ramo', 'todos_ramos', 'deletar_ramo_por_id']