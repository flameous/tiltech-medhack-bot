# -*- coding: utf-8 -*-
import traceback

import config
import telebot
from telebot import types

import models

bot = telebot.TeleBot(config.token)

#ЛВЧ вспышка базы
@bot.message_handler(commands=["reset"])
def reset_database(message):
    uid = message.chat.id
    logic.reset()
    bot.send_message(uid, "База очищена, прошлое забыто!", reply_markup=types.ReplyKeyboardRemove())

#Получение сообщения
@bot.callback_query_handler(func=lambda call: True)
def foo(call):
    uid, message = call.message.chat.id, call.data
    meta_handler(uid, message)

#Отправка сообщения
@bot.message_handler(content_types=["text"])
def handle(message):
    uid, message = message.chat.id, message.text
    meta_handler(uid, message)

#Кнопки
def meta_handler(uid: int, message: str, **kwargs):
    markup = types.ReplyKeyboardRemove()
    try:
        answer, buttons = logic.handle(uid, message)
        if buttons:
            markup = buttons

    except BaseException as e:
        answer = "Ошибка! : %s" % e
        traceback.print_tb(e.__traceback__)

    bot.send_message(uid, answer, reply_markup=markup)

    # @bot.message_handler(commands = ['url'])
    # def url(message):
    # markup = types.InlineKeyboardMarkup()
    # btn_my_site= types.InlineKeyboardButton(text='Наш сайт', url='https://habrahabr.ru')
    # markup.add(btn_my_site)
    # bot.send_message(message.chat.id, "Нажми на кнопку и перейди на наш сайт.", reply_markup = markup)


if __name__ == '__main__':
    d = models.Database()
    logic = models.Logic(d)
    bot.polling(none_stop=True)
