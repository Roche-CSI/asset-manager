import os

from flask import Flask, abort, request, g
from flask_cors import CORS

from server_core.configs import Configs
from server_core.configs.configs import ConfigModes
from server_core.db import get_db
from server_core.elastic.asset_entry import AssetEntry
from server_core.elastic.vector_search import ElasticVectorSearch
from server_core.models import create_tables
from server_core.plugins import register_plugins
from server_core.views import register_blueprints
from server_core.views.admin_views.login_admin import init_login
from server_core.views.auth_views.auth_utils import get_user_from_token


def create_app() -> Flask:
    """ Creates Flask app and database connection
    Returns
    -------
    app: Flask app
    database

    """
    app = Flask(__name__)
    configure_app(app)
    configure_database(app)
    configure_auth(app)
    configure_routes(app)
    configure_elastic(app)
    configure_cors(app)
    register_plugins()
    init_login(app)
    return app


def configure_app(app: Flask):
    """Configures the application settings."""
    if not os.getenv('APP_SECRET'):
        raise ValueError("APP_SECRET environment variable is required")
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=None,  # cross site allowed
        SECRET_KEY=os.getenv('APP_SECRET')
    )


def configure_database(app: Flask):
    """Sets up the database configuration."""
    database = get_db(app=app)
    create_tables(database=database)

    @app.before_request
    def before_request():
        database.connect(reuse_if_open=True)

    @app.after_request
    def after_request(response):
        database.close()
        return response

    app.db = database


def configure_auth(app: Flask):
    """Configures authentication middleware."""

    # List of public endpoints
    public_endpoints = {
        'static',
        'favicon',
        'health',
        'index'
    }

    # Endpoints starting with these prefixes will be public
    public_prefixes = {
        "hello_world",
        "static",
        "cli_auth_view",
        "auth_view.login",
        "auth_view.signup",
        "auth_view.callback",
        "auth_view.token_login",
        "auth_view.index",
    }

    @app.before_request
    def authenticate_request():
        # print(f"Path: {request.path}")
        # print(f"Endpoint: {request.endpoint}")
        # print(f"Blueprint: {request.blueprint}")

        # Special handling: Flask-Admin handle its own authentication
        if request.path.startswith('/admin'):
            return

        if request.endpoint is None:
            abort(404, "Endpoint not found")
        # Skip authentication for exact match public endpoints
        if request.endpoint in public_endpoints:
            return
        # Skip authentication for endpoints starting with public prefixes
        if any(request.endpoint.startswith(prefix) for prefix in public_prefixes):
            return

        request_type = type_of_request(request)
        if request_type == 'default':
            print("Message: request from older client version or local dashboard")
            return

        token = extract_token(request)
        if not token:
            abort(401, "Missing or invalid Authorization token")
        try:
            user = get_user_from_token(token)
            g.user = user.username or request.args.get('user')
        except Exception as e:
            abort(401, f"Invalid token: {str(e)}")


def type_of_request(request):
    """Returns the type of request."""
    if request.cookies.get('jwt'):
        return 'web'
    if request.headers.get("Authorization"):
        return "api"
    return 'default'


def extract_token(request):
    """Extracts the token from the request headers or cookies."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split("Bearer ")[1]
    return request.cookies.get('jwt')


def configure_routes(app: Flask):
    """Registers the application routes."""

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    register_blueprints(app)


def configure_elastic(app: Flask):
    """Configures the elastic search engine if available."""
    elastic_host = os.getenv("ELASTIC_HOST")
    if elastic_host:
        try:
            search_engine = ElasticVectorSearch.shared(host=elastic_host)
            AssetEntry.create_index(es=search_engine)
            app.search_engine = search_engine
        except Exception as e:
            print(f"Error creating search engine or its index: {str(e)}")
            app.search_engine = None


def configure_cors(app: Flask):
    """Configures CORS for the application."""
    # Retrieve extra allowed origins from an environment variable and split to get a list
    extra_allowed_origins_var = os.getenv('ASSET_EXTRA_ALLOWED_ORIGINS', '')
    extra_allowed_origins = extra_allowed_origins_var.split(',') if extra_allowed_origins_var else []

    allowed_origins = [
        Configs.shared().frontend_url,
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        *extra_allowed_origins
    ]
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": allowed_origins}})

    @app.after_request
    def add_security_headers(response):
        origin = request.headers.get('Origin')
        headers_to_remove = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Credentials',
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Methods'
        ]
        for header in headers_to_remove:  # avoid duplicate headers
            if header in response.headers:
                del response.headers[header]

        if origin in allowed_origins:
            response.headers.set('Access-Control-Allow-Origin', origin)
            response.headers.set('Access-Control-Allow-Credentials', 'true')
            response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

        return response


def run():
    Configs.shared()  # default is DEV
    is_production: bool = Configs.shared().MODE == ConfigModes.PRODUCTION
    create_app().run(debug=False if is_production else True)


if __name__ == '__main__':
    run()
