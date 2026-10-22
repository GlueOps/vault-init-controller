FROM python:3.15.1-alpine@sha256:e85751f6fe48ddb0619557d606ad93685134347a821b85fd9cd9dfa61addb970 AS test

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt -r vault-init/requirements-dev.txt

RUN pytest vault-init/tests/

FROM python:3.15.1-alpine@sha256:e85751f6fe48ddb0619557d606ad93685134347a821b85fd9cd9dfa61addb970

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]
