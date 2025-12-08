FROM python:3.14.2-alpine@sha256:f74e244c26cf94c81a2a6ec8e4e5e55e59bae979063c83382cafb87f03fc1f56

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

