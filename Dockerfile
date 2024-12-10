FROM python:3.12.8-alpine@sha256:fd340d298d9d537a33c859f03bcc60e8e2542968e16f998bb0e232e25b4b23bd

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

