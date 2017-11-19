# -*- coding: utf-8 -*-
import traceback

import telebot
from telebot import types
import sys
import models
import config
from subprocess import Popen
from flask import Flask, request, abort

app = Flask(__name__)

bot_token = config.token
if len(sys.argv) > 1:
    bot_token = config.token_fanzil

bot = telebot.TeleBot(bot_token)

PORT = 8443
WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key
WEBHOOK_URL_BASE = 'https://80.211.129.44:%s' % PORT
WEBHOOK_URL_PATH = '/%s/' % bot_token


@app.route("/")
def index():
    return "index"


@app.route("/chat", methods=["POST"])
def handle_chat():
    form = request.form
    uid = form.get('uid')
    text = form.get('text')
    bot.send_message(int(uid), text + "\n\nОтвет кейс-менеджера", reply_markup=logic.markup_button_back())
    return "ok"


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(commands=['start'])
def start_conversation(message):
    msg, buttons = logic.handle_start()
    bot.send_message(message.chat.id, msg, reply_markup=buttons)


@bot.message_handler(content_types=['contact'])
def handle_contact_number(message):
    uid, contact = message.chat.id, message.contact.phone_number
    bot.send_message(uid, "Спасибо", reply_markup=types.ReplyKeyboardRemove())

    msg, markup = logic.handle_save_number(uid, contact)
    bot.send_message(uid, msg, reply_markup=markup)


# TODO: Встроить CV
@bot.message_handler(content_types=['photo'])
def handle_pictures(message):
    answer = 'Ваш файл обработан!'
    try:
        url = bot.get_file(message.photo[-1].file_id).file_path
        fp = url.split("/")[-1]
        with open(fp, 'wb') as file:
            file.write(bot.download_file(url))
            Popen(["./example.sh", fp]).wait()

        with open(fp, 'rb') as file:
            bot.send_photo(message.chat.id, file)
    except Exception as e:
        answer = 'failed! : %s' % e
    bot.send_message(message.chat.id, answer)


# dev feature
@bot.message_handler(commands=["reset"])
def reset_database(message):
    uid = message.chat.id
    logic.reset()
    bot.send_message(uid, "База очищена, прошлое забыто!", reply_markup=types.ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    uid, message = call.message.chat.id, call.data
    meta_handler(uid, message)


@bot.message_handler(content_types=["text"])
def handle(message):
    uid, message = message.chat.id, message.text
    meta_handler(uid, message)


def meta_handler(uid: int, message: str):
    markup = types.ReplyKeyboardRemove()
    try:
        answer, buttons = logic.handle(uid, message)
        if buttons:
            markup = buttons

    except BaseException as e:
        answer = "Ошибка! : %s" % e
        traceback.print_tb(e.__traceback__)

    if answer:
        bot.send_message(uid, answer, reply_markup=markup)


if __name__ == '__main__':
    d = models.Database()
    logic = models.Logic(d)
    bot.remove_webhook()

    if len(sys.argv) == 1:
        bot.polling(none_stop=True)
    else:

        bot.set_webhook(
            url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
            certificate=open(WEBHOOK_SSL_CERT, 'r')
        )

        app.run(
            host="0.0.0.0",
            port=PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
        )
