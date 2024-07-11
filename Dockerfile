FROM python:3.11.9-alpine@sha256:eb8afe385f10ccc9da8378e8712fea8b26f4ed009648f8afea4518836d8b3ed3

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

