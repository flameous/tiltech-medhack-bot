# -*- coding: utf-8 -*-
import config
import telebot

import models

bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    uid, text = message.chat.id, message.text
    answer = logic.handle(uid, text)
    bot.send_message(uid, answer)


if __name__ == '__main__':
    d = models.Database()
    logic = models.Logic(d)
    bot.polling(none_stop=True)
