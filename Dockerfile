# Use a imagem base do Python 3.12.3
FROM python:3.12.3

# Defina o diretório de trabalho como /app
WORKDIR /app

# Copie o código do diretório atual para /app no contêiner
COPY . /app

# Crie e ative o ambiente virtual
RUN python3 -m venv venv

# Instale as dependências dentro do ambiente virtual
RUN /bin/bash -c "source venv/bin/activate && pip install --no-cache-dir -r requirements.txt"

# Exponha a porta 8001 (opcional, dependendo do uso)
EXPOSE 8001

# Defina o comando padrão para iniciar o servidor usando Gunicorn
CMD ["venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:8001", "--timeout", "120", "run:app"]