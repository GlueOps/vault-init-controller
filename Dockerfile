FROM python:3.13.1-alpine@sha256:804ad02b9ba67ea1f8307eeb6407b121c6bd6bb19d3f182aae166821eb59d6a4

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

