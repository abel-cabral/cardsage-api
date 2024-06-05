import os
from datetime import timedelta

class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 30)))
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    # Adicione outras configurações aqui, se necessário
    
__all__ = ['Config']