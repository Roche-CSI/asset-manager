import flask_login as login
from server_core import models
from wtforms import form, fields, validators


class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.InputRequired()])
    token = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_token(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.token != self.token.data:
            raise validators.ValidationError('Invalid token')

    def get_user(self):
        return models.User.get_if_exists(models.User.email == self.email.data.strip(),
                                         models.User.token == self.token.data.strip())


def init_login(app):
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return models.User.get(models.User.id == user_id)
        except Exception as e:
            return None
