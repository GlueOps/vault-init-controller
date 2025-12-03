FROM python:3.14.1-alpine@sha256:4f699e4afac838c50be76deac94a6dde0e287d5671fd8e95eb410f850801b237

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

