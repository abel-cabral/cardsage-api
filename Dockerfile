# Use a imagem oficial do Python como base
FROM python:3.12-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instale dependências adicionais do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copie o arquivo de dependências para o contêiner
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie o restante do código do aplicativo para o contêiner
COPY . .

# Exponha a porta em que o aplicativo será executado
EXPOSE 8001

# Comando para rodar o aplicativo Flask usando gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8001", "run:app"]
