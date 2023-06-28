FROM python:3.10-alpine

WORKDIR /app

RUN python3 -m pip install --upgrade pip setuptools wheel

COPY setup.py .
COPY gunicorn_conf.py .
COPY obelisk/ obelisk/

RUN python3 -m pip install .

CMD gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py obelisk.app:app