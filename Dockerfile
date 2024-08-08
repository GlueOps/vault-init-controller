FROM python:3.12.5-alpine@sha256:c2f41e6a5a67bc39b95be3988dd19fbd05d1b82375c46d9826c592cca014d4de

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

