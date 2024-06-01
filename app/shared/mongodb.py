import os
from pymongo import MongoClient
from dotenv import load_dotenv

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

# Apenas 'collection' será exportado quando importado de outro script
__all__ = ['collection']