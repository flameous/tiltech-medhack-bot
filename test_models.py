import unittest

import models


def raise_foo():
    raise BaseException("sada")


class TestDatabase(unittest.TestCase):
    db = models.Database()

    def test_none_user(self):
        with self.assertRaises(BaseException):
            self.db.get_user()

        u1 = self.db.get_user(10)
        print('db get_user by id 1 -- ', u1)
        self.assertIsNone(u1)

        u2 = self.db.get_user('test_login')
        print('db get_user by login "test_user_login" -- ', u2)
        self.assertIsNone(u2)

    def test_save_user(self):
        u = models.User(100, "login_foo", models.state_new_user)
        self.db.save_user(u)

    def test_get_existed_user(self):
        u1 = self.db.get_user(100)
        print('db get_user by id 100 -- %s' % u1)
        self.assertIsNotNone(u1)

        u2 = self.db.get_user(login='login_foo')
        print('db get_user by login "login_foo" -- ', u2)
        self.assertIsNotNone(u2)


if __name__ == '__main__':
    unittest.main()
