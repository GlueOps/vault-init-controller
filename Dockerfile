FROM python:3.11.8-alpine@sha256:b6bd7d58b4e0f38cd151de9b96fffc9edf647bc6ba490ffe772d5d5eab11acda

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

