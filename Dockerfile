FROM python:3.13.7-alpine@sha256:587df003ff48316a56a0ddac50e1e2b64dfeca281f0c071b91920895a65b12d2

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

