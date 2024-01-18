FROM python:alpine

WORKDIR /usbot

COPY app .

RUN pip install -r requirments.txt

RUN sudo echo -e "192.168.100.223 us3.radionet.com.ua\n10.255.255.234 bill-admin2.radionet.com.ua" >> /etc/hosts

ENTRYPOINT [ "python", "telegram_bot.py" ]