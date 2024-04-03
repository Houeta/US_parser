FROM python:alpine

ARG user
ARG pass
ARG API_TELEGRAM

ENV user=${user}
ENV pass=${pass}
ENV API_TELEGRAM=${API_TELEGRAM}

WORKDIR /usbot

COPY app .

RUN pip install -r requirments.txt

ENTRYPOINT [ "python", "telegram_bot.py" ]