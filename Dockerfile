FROM python:3.14.9-alpine@sha256:d55673c233e28839c1c0c69766428cb6d50174a2ecfdcf915b6f58a0b0991562 AS test

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt -r vault-init/requirements-dev.txt

RUN pytest vault-init/tests/

FROM python:3.14.9-alpine@sha256:d55673c233e28839c1c0c69766428cb6d50174a2ecfdcf915b6f58a0b0991562

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]
