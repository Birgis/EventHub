from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, name, email, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
