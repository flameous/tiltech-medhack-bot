import requests
import json

from telebot import types

state_chatting = 'state_chatting'
state_menu = 'state_menu'

button_open_jira = 'Открыть веб-интерфейс'
button_chat = 'Чат со специалистом'
button_back_to_menu = 'Закрыть чат'

ikb = types.InlineKeyboardButton


class User:
    def __init__(self, tg_id: int, state: str, mobile_number: int):
        self.tg_id = tg_id
        self.state = state
        self.mobile_number = mobile_number

    def __str__(self):
        return self.dump()

    def dump(self) -> str:
        return json.dumps({
            "uid": self.tg_id,
            "state": self.state,
            "mobile_number": self.mobile_number
        })


class Database:
    def __init__(self, addr_port: str = "http://80.211.129.44:8100/user"):
        """
        Обёртка для БД
        :param addr_port: адрес и порт удалённого сервера с БД
        """
        self.addr_port = addr_port
        self.dict = {}

    def get_user(self, tg_id: int) -> User:
        return self.dict.get(tg_id, None)

        r = requests.get(self.addr_port + str(tg_id))
        if r.status_code not in (200, 404):
            raise BaseException('/get_user error, response text: -- ' + r.text)

        if r.status_code == 404:
            return None

        data = json.loads(r.text)
        u = User(
            data['tg_id'],
            data['state'],
            data['mobile_number']
        )
        return u

    def save_user(self, u: User):
        return self.dict.update({u.tg_id: u})

        r = requests.post(self.addr_port + str(u.tg_id), data={"user": u.dump()})
        if r.status_code != 200:
            raise BaseException('save user error, response text: --' + r.text)
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
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton('Отправить номер', request_contact=True))
        return "Чтобы работать в нашей системе, надо дать согласие на ...\n" \
               "Разрешите получить ваш номер телефона", markup

    def handle_save_number(self, uid, contact):
        self.db.save_user(User(uid, state_menu, contact))
        return self.menu()

    @staticmethod
    def menu():
        markup = types.InlineKeyboardMarkup()
        markup.row(*[ikb(button_chat, callback_data=button_chat)])
        markup.row(*[ikb(button_open_jira, callback_data=button_open_jira, url="http://panacea.cloud/")])
        markup.row(*[ikb(button_back_to_menu, callback_data=button_back_to_menu)])
        return "Добро пожаловать в систему!", markup

    @staticmethod
    def markup_button_back():
        markup = types.InlineKeyboardMarkup()
        markup.add(ikb(button_back_to_menu, callback_data=button_back_to_menu))
        return markup

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
            return self.handle_start()

        if message == button_back_to_menu:
            self.set_state_and_save(u, state_menu)
            return self.menu()

        if u.state == state_chatting:
            return self.handle_chat(uid, message)

        if message == button_chat:
            self.set_state_and_save(u, state_chatting)
            return "Сейчас с вами свяжется кейс-менеджер >%s<" % str(uid), None

        return self.menu()

    def reset(self):
        self.db.reset()
        pass

    @staticmethod
    def handle_chat(uid, message):
        requests.post('http://80.211.129.44:8100/send_to_chat', data={"uid": uid, "message": message})
        return None, None
