from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

class User(UserMixin):
    def __init__(self, id, names, email,password):
        self.id = str(id)
        self.email = email
        self.names = names
        self.password = password
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def get_names(self):
        return self.names

    def get_data(self):
        return {'id': self.id, 'names': self.names, 'email': self.email}


