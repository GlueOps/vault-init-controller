FROM python:3.11.12-alpine@sha256:32ac7ba3dad4bcee9c8cfaf3b489f832b84ba0a1eb8ef76685456d424baaf444

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

