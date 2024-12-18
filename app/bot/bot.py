#!/usr/bin/env python
from telebot import TeleBot
from bot.handlers import register_handlers
from bot.config import API_TOKEN

bot = TeleBot(API_TOKEN)

register_handlers(bot)

if __name__ == '__main__':
    bot.infinity_polling()
    