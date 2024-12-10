FROM python:3.13.1-alpine@sha256:5dad625efcbc6fad19c10b7b2bfefa1c7a8129c8f8343106b639c27dd9e7db2c

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

