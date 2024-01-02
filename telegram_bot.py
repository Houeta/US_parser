#!/usr/bin/env python
import os
import subprocess
import time

from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv('.env')
API_TOKEN = os.environ.get('API_TELEGRAM')
bot = TeleBot(API_TOKEN)
is_auth = False
@bot.message_handler(commands=['authorize'])
def enter_password(message):
    password = bot.send_message(message.chat.id, 'Це приватний бот, для продовження введи пароль.')
    bot.register_next_step_handler(password, auth_password)
    
def auth_password(message):
    if message.text == 'GAY':
        start_date = bot.send_message(message.chat.id, 'Авторизація успішна.\n Вкажіть початкову дату y форматі <dd>.<mm>.<yy>')
        start = start_date.text
        is_auth = True
        bot.register_next_step_handler(start_date, get_end_date)
    else: 
        bot.send_message(message.chat.id, 'Incorrect Password')
        is_auth = False
        bot.register_next_step_handler(message, enter_password)

def get_end_date(message):
    start_date = message.text
    end_date = bot.send_message(message.chat.id, 'Введіть кінцеву дату y форматі <dd>.<mm>.<yy>\n Зробіть паузу в 3-5с. та виконайте /get_excel')
    bot.register_next_step_handler(end_date, start_script, start_date)

def start_script(message, start):
    global path_to_file
    path_to_file = f"excel_data/tasks-{start}-{message.text}.xlsx"
    if os.path.exists(path_to_file):
        bot.send_message(message.chat.id, 'File was created before..\n Enter /get_excel for download file.')
    else:
        subprocess.run(["python", "parse.py", f"--start={start}", f"--end={message.text}"])
        time.sleep(5)
    bot.register_next_step_handler(message, get_excel)  
    

@bot.message_handler(commands=['start', 'help'])  #Respond to request
def send_welcome(message):
    fname = '' if message.from_user.first_name == None else message.from_user.first_name
    lname = '' if message.from_user.last_name == None else message.from_user.last_name
    bot.send_message(message.chat.id, f'Привіт, {fname} {lname}!')
    if not is_auth:
        enter_password(message)

@bot.message_handler(commands=['get_excel'])
def get_excel(message):
    
    bot.send_message(message.chat.id, f'Файл вивантажується')
    try:
        bot.send_document(message.chat.id, types.InputFile(path_to_file))
    except:
        bot.send_message(message.chat.id, f'Файл {path_to_file} не знайдено.')   

@bot.message_handler(commands=['currency'])
def choose_currency(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_usd = types.InlineKeyboardButton('🇺🇸 USD', callback_data='usd')
    btn_eur = types.InlineKeyboardButton('🏳️‍🌈 EUR', callback_data='eur')
    btn_yen = types.InlineKeyboardButton('🇯🇵 YEN', callback_data='jpy')
    btn_vnd = types.InlineKeyboardButton('🇻🇳 VND', callback_data='vnd')
    markup.add(btn_usd, btn_eur, btn_yen, btn_vnd)
    bot.send_message(message.chat.id, f'Choose currency', reply_markup=markup)

    
bot.infinity_polling()