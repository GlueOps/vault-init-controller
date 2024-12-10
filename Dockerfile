FROM python:3.11.11-alpine@sha256:9ae1ab261b73eeaf88957c42744b8ec237faa8fa0d5be22a3ed697f52673b58a

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

