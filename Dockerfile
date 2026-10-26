FROM python:3.15.2-alpine@sha256:827d76cd0da4f700a703df95e7a70fec2ecc7fa9fd528638ab2e8aa96fbf8e0e AS test

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt -r vault-init/requirements-dev.txt

RUN pytest vault-init/tests/

FROM python:3.15.2-alpine@sha256:827d76cd0da4f700a703df95e7a70fec2ecc7fa9fd528638ab2e8aa96fbf8e0e

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]
