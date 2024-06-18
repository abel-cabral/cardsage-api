FROM python:3.9

WORKDIR /app

# Copie os arquivos necessários para o diretório de trabalho do contêiner
COPY . .

# Instale a biblioteca dotenv
RUN pip install python-dotenv

# Instale as dependências Python
RUN pip install -r requirements.txt

# Exponha a porta que sua aplicação estará ouvindo
EXPOSE 8001

# Carregar variáveis de ambiente do arquivo .env e iniciar o servidor
CMD ["python", "-c", "import dotenv; dotenv.load_dotenv('.env'); import os; os.system('gunicorn -w 4 -b 0.0.0.0:8001 run:app')"]