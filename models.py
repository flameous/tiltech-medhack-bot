import requests
import json
from text import *

from telebot import types

state_user_is_first_time = "state_user_terms_undefined"
state_user_next_stage = "state_user_terms_agree"
state_user_terms_disagree = "state_user_terms_disagree"
state_user_cm_visit = "state_user_cm_visit"
state_user_old = "state_user_old"
state_user_live_meeting_md = "state_user_live_meeting_md"
state_user_video_call = "state_user_video_call"
state_user_phone_call = "state_user_phone_call"
state_user_im_cm_chat = "state_user_im_cm_chat"
state_user_select_consultant = "state_user_select_consultant"
state_user_send_photo = "state_user_send_photo"

state_user_register = 'state_user_register'

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
back = 'Назад'
add_cart = 'Добавить направление'
all_cart = 'Все направления'

buttons_data = {v: 'button_' + str(k) for k, v in enumerate((agree, disagree, open_jira, change_opinion, reset, yes, no,
                                                             send_pic, im_cm, live_meeting_md, video_call, phone_call,
                                                             im_cm_chat, back, add_cart, all_cart, chat_with_cm))}


def row_inline(markup, rows):
    for row in rows:
        markup.row(*[types.InlineKeyboardButton(b, callback_data=buttons_data[b]) for b in row])


def row_reply(markup, rows):
    for row in rows:
        markup.row(*[types.KeyboardButton(b) for b in row])


# generate_buttons([A, B, C], [D, E])
# [A - B - C]
# [D ----- E]
def generate_buttons(*rows, inline=True):
    if inline:
        markup = types.InlineKeyboardMarkup()
        f = row_inline
    else:
        markup = types.ReplyKeyboardMarkup()
        f = row_reply

    f(markup, rows)
    return markup


buttons_is_first_time = generate_buttons([yes, no], inline=False)
buttons_send_pic_or_im_cm = generate_buttons([send_pic], [im_cm], [add_cart], [all_cart])
buttons_consultation = generate_buttons([live_meeting_md], [video_call], [phone_call], [im_cm_chat])
buttons_no = generate_buttons([no])
buttons_back = generate_buttons([back])


class User:
    def __init__(self, uid: int, login: str = "no_login", state: str = "state_new_user"):
        self.uid = uid
        self.state = state
        self.verified = False

    def __str__(self):
        return self.dump()

    def dump(self) -> str:
        return json.dumps({
            "uid": self.uid,
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

    def save_contact_number(self, uid, number):
        return


class Logic:
    def __init__(self, db: Database):
        self.db = db
        pass

    def set_state_and_save(self, u: User, state: str):
        u.state = state
        self.db.save_user(u)

    @staticmethod
    def handle_start():
        return text_hello, generate_buttons([chat_with_cm], inline=False)

    @staticmethod
    def handle_get_number():
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton('Отправить', request_contact=True))
        return "Разрешите получить ваш номер телефона", markup

    def handle_contact_number(self, uid, contact):
        self.db.save_contact_number(uid, contact)
        return "contact handler"

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
            # если это новый юзер, то запрашиваем его номер
            self.db.save_user(User(uid, state=state_user_is_first_time))
            return self.handle_get_number()

        if u.state == state_user_next_stage:
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

        # if message == buttons_data[back]:
        #     self.set_state_and_save(u, state_user_next_stage)
        #     return text_thanks_and_how_help, buttons_send_pic_or_im_cm

        if u.state == state_user_next_stage:
            if message == buttons_data[im_cm]:
                self.set_state_and_save(u, state_user_select_consultant)
                return text_consultant, buttons_consultation
            elif message == buttons_data[send_pic]:
                self.set_state_and_save(u, state_user_send_photo)
                return text_send_photo, None

        if u.state == state_user_select_consultant:

            if message == buttons_data[live_meeting_md]:
                self.set_state_and_save(u, state_user_live_meeting_md)
                return choose_time, None
            elif message == buttons_data[video_call]:
                self.set_state_and_save(u, state_user_video_call)
                return text_video_call, None
            elif message == buttons_data[phone_call]:
                self.set_state_and_save(u, state_user_phone_call)
                return text_phone_call, None
            elif message == buttons_data[im_cm_chat]:
                self.set_state_and_save(u, state_user_im_cm_chat)
                return nepridumal, None

        # юзер не подтвердил свою личность (фотка паспорта / другое)
        if not u.verified:
            pass

        # --- конец логики
        return "Раздел в разработке, нажмите /reset чтобы вернуться назад " \
               "\n" \
               ": '%s'" % message, None

    def reset(self):
        self.db.reset()
        pass

    def handle_chat(self, uid, text):
        pass
