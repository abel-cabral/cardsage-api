# Use a imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências para o contêiner
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código do aplicativo para o contêiner
COPY . .

# Exponha a porta em que o aplicativo será executado
EXPOSE 8001

# Comando para rodar o aplicativo Flask usando gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8001", "app:app"]