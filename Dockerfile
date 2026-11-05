FROM python:3.15.2-alpine@sha256:2b4b04f31a4a009c1fadf7ce9338471f288488199cf43dcd1af71f244ea550aa AS test

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt -r vault-init/requirements-dev.txt

RUN pytest vault-init/tests/

FROM python:3.15.2-alpine@sha256:2b4b04f31a4a009c1fadf7ce9338471f288488199cf43dcd1af71f244ea550aa

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]
