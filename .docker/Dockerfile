FROM python:3.10-alpine

ARG user
ARG pass
ARG API_TELEGRAM

ENV user=${user} \
    pass=${pass} \
    API_TELEGRAM=${API_TELEGRAM}

WORKDIR /app

COPY app .

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev && \
    pip install --no-cache-dir -r requirments.txt

RUN python -m compileall .

ENTRYPOINT [ "python", "bot/bot.py" ]