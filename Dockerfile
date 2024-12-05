FROM python:3.11.11-alpine@sha256:fbcb089a803d5673f225dc923b8e29ecc7945e9335465037b6961107b9da3d61

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

