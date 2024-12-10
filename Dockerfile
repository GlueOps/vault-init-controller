FROM python:3.12.8-alpine@sha256:b0fc5cb1a4ae39af99c0ddf4b56cb06e8f867dce47fa9a8553f8601e527596b4

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

