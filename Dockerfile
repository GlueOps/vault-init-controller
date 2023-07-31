FROM python:3-alpine

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python3", "/app/vault-init/main.py"]

