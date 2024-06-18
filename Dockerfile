FROM python:3.12.3

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

# Defina a porta que você deseja expor
EXPOSE 8001

# CMD deve ser definido como uma lista de strings separadas
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8001", "--timeout", "120", "run:app"]