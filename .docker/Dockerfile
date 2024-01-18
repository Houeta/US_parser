FROM python:alpine

WORKDIR /usbot

COPY app .

RUN pip install -r requirments.txt

ENTRYPOINT [ "python", "telegram_bot.py" ]