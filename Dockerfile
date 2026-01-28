FROM python:3.14.2-alpine@sha256:59d996ce35d58cbe39f14572e37443a1dcbcaf6842a117bc0950d164c38434f9

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

