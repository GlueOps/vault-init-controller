FROM python:3.11.11-alpine@sha256:9af3561825050da182afc74b106388af570b99c500a69c8216263aa245a2001b

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

