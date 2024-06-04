import os
class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # Adicione outras configurações aqui, se necessário