from .python_client_views import register_blueprints as pc_blue_prints
from .js_client_views import register_blueprints as dashboard_blue_prints
from .admin_views import register_blueprints as admin_blue_prints
from .auth_views import register_blueprints as auth_blue_prints


def register_blueprints(app):
    pc_blue_prints(app)
    dashboard_blue_prints(app)
    admin_blue_prints(app)
    auth_blue_prints(app)
