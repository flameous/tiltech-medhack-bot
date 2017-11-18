from telebot import types

import requests
import json
from text import *

state_user_terms_undefined = "state_user_terms_undefined"
state_user_terms_agree = "state_user_terms_agree"
state_user_terms_disagree = "state_user_terms_disagree"
state_user_cm_visit = "state_user_cm_visit"
state_user_old = "state_user_old"
state_user_live_meeting_md  = "state_user_live_meeting_md"
state_user_video_call  = "state_user_video_call"
state_user_phone_call  = "state_user_phone_call"
state_user_im_cm_chat  = "state_user_im_cm_chat"
state_user_select_consultant = "state_user_select_consultant"
state_user_send_photo = "state_user_send_photo"


agree = 'Согласен'
disagree = 'Не согласен'
chat_with_cm = 'Связаться с кейс-менеджером'
open_jira = 'Открыть веб-интерфейс'
change_opinion = 'Я передумал!'
reset = 'reset!'
yes = 'Да, лечился раньше'
no = 'Нет, я впервые'
send_pic = 'Отправить результаты анализов для оцифровки'
im_cm = 'Проконсультироваться с врачом(кейс менеджером)'
live_meeting_md = 'Прийти на очный прием'
video_call = 'Видеосвязь'
phone_call = 'Созвониться по телефону'
im_cm_chat = 'Чат со специалистом'
<<<<<<< HEAD
back = 'Назад'
add_cart = 'Добавить направление'
all_cart = 'Все направления'

buttons_data = {v: 'button_'+str(k) for k, v in enumerate((agree, disagree, open_jira, change_opinion, reset, yes, no, send_pic, im_cm, live_meeting_md, video_call, phone_call, im_cm_chat, back, add_cart, all_cart))}
=======


buttons_data = {v: 'button_'+str(k) for k, v in enumerate((agree, disagree, open_jira, change_opinion, reset, yes, no, send_pic, im_cm, live_meeting_md, video_call, phone_call, im_cm_chat))}
>>>>>>> 34f4098eb4ac1bb0355e031a06ed1881b48df8ad

buttons_terms = types.InlineKeyboardMarkup()
buttons_terms.row(types.InlineKeyboardButton('terms of use', url='http://google.com'))
buttons_terms.row(types.InlineKeyboardButton(agree, callback_data=buttons_data[agree]),
                  types.InlineKeyboardButton(disagree, callback_data=buttons_data[disagree]))
buttons_terms2 = types.InlineKeyboardMarkup()
buttons_terms2.row(types.InlineKeyboardButton(yes, callback_data=buttons_data[yes]),
                  types.InlineKeyboardButton(no, callback_data=buttons_data[no]))
buttons_send_pic_or_im_cm = types.InlineKeyboardMarkup()
buttons_send_pic_or_im_cm.row(types.InlineKeyboardButton(send_pic, callback_data=buttons_data[send_pic]))
buttons_send_pic_or_im_cm.row(types.InlineKeyboardButton(im_cm, callback_data=buttons_data[im_cm]))
# buttons_send_pic_or_im_cm.row(types.InlineKeyboardButton(add_cart, callback_data=buttons_data[add_cart]))
# buttons_send_pic_or_im_cm.row(types.InlineKeyboardButton(all_cart, callback_data=buttons_data[all_cart]))


buttons_no = types.InlineKeyboardMarkup()
buttons_no.row(types.InlineKeyboardButton(no, callback_data=buttons_data[no]))

buttons_consultation = types.InlineKeyboardMarkup()
buttons_consultation.row(types.InlineKeyboardButton(live_meeting_md, callback_data=buttons_data[live_meeting_md]))
buttons_consultation.row(types.InlineKeyboardButton(video_call, callback_data=buttons_data[video_call]))
buttons_consultation.row(types.InlineKeyboardButton(phone_call, callback_data=buttons_data[phone_call]))
buttons_consultation.row(types.InlineKeyboardButton(im_cm_chat, callback_data=buttons_data[im_cm_chat]))

<<<<<<< HEAD
buttons_back = types.InlineKeyboardMarkup()
buttons_back.row(types.InlineKeyboardButton(back, callback_data=buttons_data[back]))
=======

>>>>>>> 34f4098eb4ac1bb0355e031a06ed1881b48df8ad
class User:
    def __init__(self, uid: int, login: str = "no_login", state: str = "state_new_user"):
        self.uid = uid
        self.login = login
        self.state = state
        self.verified = False

    def __str__(self):
        return self.dump()

    def dump(self) -> str:
        return json.dumps({
            "uid": self.uid,
            "login": self.login,
            "state": self.state,
            "verified": self.verified,
        })


class Database:
    def __init__(self, addr_port: str = "http://80.211.129.44:8100/bot"):
        """
        Обёртка для БД
        :param addr_port: адрес и порт удалённого сервера с БД
        """
        self.addr_port = addr_port

    def get_user(self, uid=None, login=None) -> User:
        """
        Достаём юзера из удалённой БД
        :param uid:
        :param login:
        :return:
        """
        if not uid and not login:
            raise BaseException("use uid OR login")

        url = "/get_user"
        if uid:
            params = {"uid": uid}
        else:
            params = {"login": login}

        r = requests.get(self.addr_port + url, params=params)
        if r.status_code not in (200, 404):
            raise BaseException('/get_user error, response text: -- ' + r.text)

        if r.status_code == 404:
            return None

        data = json.loads(r.text)
        u = User(
            data['uid'],
            data['login'],
            data['state']
        )
        return u

    def save_user(self, u: User):
        r = requests.post(self.addr_port + '/save_user', data={"user": u.dump()})
        if r.status_code != 200:
            raise BaseException('/save_user error, response text: --' + r.text)
        return

    def reset(self):
        requests.post(self.addr_port + '/reset')


class Logic:
    def __init__(self, db: Database):
        self.db = db
        pass

    def set_state_and_save(self, u: User, state: str):
        u.state = state
        self.db.save_user(u)

    def handle(self, uid: int, message: str) -> tuple:
        """
        Общая логика бота

        :param uid: id юзера
        :param message: его сообщение
        :return: сообщение, отсылаемое юзеру (опционально: кнопки)
        """

        # достаём юзера
        u = self.db.get_user(uid)
        if not u:
            # если это новый юзер
            self.db.save_user(User(uid, state=state_user_terms_undefined))
            # сохраняем юзера в бд и возвращаем приветствие
            return text_hello, buttons_terms2

        if u.state == state_user_terms_undefined:
            if (message == buttons_data[no]) or (message == buttons_data[back]):
                self.set_state_and_save(u, state_user_terms_agree)
                return text_thanks_and_how_help, buttons_send_pic_or_im_cm


            elif message == buttons_data[yes]:
                self.set_state_and_save(u, state_user_terms_undefined)
                return text_no_support, buttons_no



        if u.state == state_user_terms_agree:
            if message == buttons_data[im_cm]:
                self.set_state_and_save(u, state_user_select_consultant)
                return text_consultant, buttons_consultation
            elif message == buttons_data[send_pic]:
                self.set_state_and_save(u, state_user_send_photo)
                return text_send_photo, buttons_back
            elif message == buttons_data[add_cart]:
                self.set_state_and_save(u, state_user_send_photo)
                return text_add_cart, buttons_back
            elif message == buttons_data[all_cart]:
                self.set_state_and_save(u, state_user_send_photo)
                return text_all_cart, buttons_back


        if u.state == state_user_select_consultant:
            if message == buttons_data[live_meeting_md]:
                self.set_state_and_save(u, state_user_live_meeting_md)
                return choose_time, buttons_back
            elif message == buttons_data[video_call]:
                self.set_state_and_save(u, state_user_video_call)
                return text_video_call, buttons_back
            elif message == buttons_data[phone_call]:
                self.set_state_and_save(u, state_user_phone_call)
                return text_phone_call, buttons_back
            elif message == buttons_data[im_cm_chat]:
                self.set_state_and_save(u, state_user_im_cm_chat)
                return nepridumal, buttons_back


        if message == buttons_data[back]:
            self.set_state_and_save(u, state_user_terms_agree)
            return text_thanks_and_how_help, buttons_send_pic_or_im_cm

        if u.state == state_user_terms_agree:
            if message == buttons_data[im_cm]:
                self.set_state_and_save(u, state_user_select_consultant)
                return text_consultant, buttons_consultation,
            elif message == buttons_data[send_pic]:
                self.set_state_and_save(u, state_user_send_photo)
                return text_send_photo,

        if u.state == state_user_select_consultant:

            if message == buttons_data[live_meeting_md]:
                self.set_state_and_save(u, state_user_live_meeting_md)
                return choose_time,
            elif message == buttons_data[video_call]:
                self.set_state_and_save(u, state_user_video_call)
                return text_video_call,
            elif message == buttons_data[phone_call]:
                self.set_state_and_save(u, state_user_phone_call)
                return text_phone_call,
            elif message == buttons_data[im_cm_chat]:
                self.set_state_and_save(u, state_user_im_cm_chat)
                return nepridumal,




        #
        # else:
        #         return text_terms_undefined,
        #
        # # --- начало
        #
        # if u.state == state_user_terms_disagree:
        #     return text_terms_rethink, buttons_terms

        # юзер не подтвердил свою личность (фотка паспорта / другое)
        if not u.verified:
            pass

        # --- конец логики
        return "Раздел в разработке, нажмите /reset чтобы вернуться назад " \
               "\n" \
               ": '%s'" % message,

    def reset(self):
        self.db.reset()
        pass
