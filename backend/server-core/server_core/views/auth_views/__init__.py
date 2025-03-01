from .web_login_view import view as web_login
from .cli_login_view import view as cli_login


def register_blueprints(app):
    app.register_blueprint(web_login, url_prefix="/auth/web")
    app.register_blueprint(cli_login, url_prefix="/auth/cli")
