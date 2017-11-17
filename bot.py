# -*- coding: utf-8 -*-
import config
import telebot

import models

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=["reset"])
def reset_database(message):
    uid = message.chat.id
    logic.reset()
    bot.send_message(uid, "База очищена, прошлое забыто!")


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    uid, text = message.chat.id, message.text
    try:
        answer = logic.handle(uid, text)
    except Exception as e:
        answer = "Ошибка! : %s" % e

    bot.send_message(uid, answer)


if __name__ == '__main__':
    d = models.Database()
    logic = models.Logic(d)
    bot.polling(none_stop=True)
