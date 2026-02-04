FROM python:3.14.3-alpine@sha256:e43b76c7e4a8a4621f4e84fd76e0dfb473eda5cc05fc58b2d4d640338eda48b1

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

