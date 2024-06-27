FROM python:3.11.9-alpine@sha256:5745fa2b8591a756160721b8305adba3972fb26a9132789ed60160f21e55f5dc

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

