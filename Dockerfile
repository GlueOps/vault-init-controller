FROM python:3.13.8-alpine@sha256:7466fcadc01effec6ae9b26f147673090a9828a16ecd7cfa5898855e3bbf12db

WORKDIR /app

COPY . /app/vault-init

RUN pip3 install -r vault-init/requirements.txt

CMD ["python", "-u", "/app/vault-init/main.py"]

