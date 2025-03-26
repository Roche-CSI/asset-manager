import datetime
import json
from typing import Optional

import google
import jwt
import requests
from flask import current_app, Response
from flask.globals import request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from werkzeug.exceptions import abort

from server_core.configs.configs import Configs
from server_core import models
from server_core.models.base.base import db_proxy as db

algorithm = "HS256"  # os.getenv("ALGORITHM")


def user_signup(data: dict, DOMAIN_VERIFICATION_REQUIRED: bool = True):
    if not data.get("username") or not data.get("email"):
        raise Exception("both email and username is required")
    # create user table entry

    DOMAIN = Configs.shared().get_domain()
    if DOMAIN_VERIFICATION_REQUIRED and DOMAIN is None:
        raise Exception("Domain can not be null")
    elif DOMAIN is None:
        print("Warning: Domain should be set before deploying to production")

    if DOMAIN not in data.get("email"):
        raise Exception("invalid email, only valid org emails are allowed")

    with db.atomic() as txn:
        user = models.User.get_if_exists(models.User.username == data.get("username"))
        if not user:
            user = models.User.create(user=data.get("username"), username=data.get("username"), email=data.get("email"))
        if user.email != data.get("email"):
            raise Exception("user data corruption, both email and username are unique keys")
        # check for default project in settings
        default_project = models.AssetSettings.default_project()
        if default_project:
            role = models.Role.create_if_not_exists_for_project(username=user.username,
                                                                project_name=default_project.name)
            user_role = models.UserRole.create_if_not_exists_for_role(username=user.username,
                                                                      role_id=role.id,
                                                                      user_id=user.id)
        return user.to_dict()


def verify_oauth2_token(token: str, client_id: str):
    request_session = requests.session()
    token_request = google.auth.transport.requests.Request(session=request_session)
    id_info = id_token.verify_oauth2_token(
        id_token=token,
        request=token_request,
        audience=client_id
    )
    return id_info


def get_flow(configs: dict = None, redirect_uri: str = None):
    """
    Get flow object for google auth
    First check if configs are provided, if not, fetch from db
    the auth config is set in AuthProvider table, named `google_auth`
    in the configs, the web key should have the `client_id, client_secret, redirect_uris, scopes`
    :param configs: dict
    :param redirect_uri: str
    :return: Flow, dict
    """
    if not configs:
        auth = models.AuthProvider.get(models.AuthProvider.name == "google_auth")
        configs = auth.configs
    flow = Flow.from_client_config(client_config=configs,
                                   scopes=configs.get("web").get("scopes"),
                                   redirect_uri=redirect_uri)
    return flow, configs


# wrapper
def login_required(function):
    def wrapper(*args, **kwargs):
        encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
        if encoded_jwt == None:
            return abort(401)
        else:
            return function()

    return wrapper


def generate_jwt(payload):
    encoded_jwt = jwt.encode(payload, current_app.secret_key, algorithm=algorithm)
    return encoded_jwt


def generate_token_with_expiry(user: dict, expiry: datetime):
    current_user = models.user.User.get_if_exists(models.user.User.email == user.get("email"))
    if user:
        login_info = {
            "user": {
                "id": str(current_user.id),
                "username": str(current_user.username),
                "email": str(current_user.email)
            },
            "exp": expiry,
        }
        jwt_token = generate_jwt(login_info)
        current_user.token = jwt_token
        current_user.save(user=current_user.username)
        return jwt_token


def get_user_from_token(token: str) -> Optional[models.user.User]:
    """
    Decode JWT token and return corresponding user.
    """
    decoded = jwt.decode(token, current_app.secret_key, algorithms=algorithm)
    user: dict = decoded.get('user')
    if not user or 'email' not in user:
        return None
    return models.user.User.get_if_exists(models.user.User.email == user.get("email"))


def validate_and_refresh_jwt(token: str):
    try:
        current_user = get_user_from_token(token)
        if not current_user:
            return Response(
                response=json.dumps({"message": "User does not exist"}),
                status=500,
                mimetype='application/json'
            )
        decoded = jwt.decode(token, current_app.secret_key, algorithms=algorithm)
        expiry = decoded.get("exp")
    except jwt.ExpiredSignatureError:
        # Signature has expired
        days = 30  # months = 6, if not refreshed, obtain new token
        expiry = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=days)
        decoded = jwt.decode(token,
                             current_app.secret_key,
                             algorithms=algorithm,
                             options={"verify_exp": False})
        token = generate_token_with_expiry(decoded.get("user"), expiry=expiry)
    result = {"token": token, "expired": False, "expiry_date": expiry, "user": decoded.get("user")}
    return Response(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )


def validate_user_data(data: dict, DOMAIN_VERIFICATION_REQUIRED: bool = True):
    """
    Checks the data returned by google auth
    :param data:
    :return:
    """
    DOMAIN = Configs.shared().get_domain()
    if DOMAIN_VERIFICATION_REQUIRED and DOMAIN is None:
        raise ValueError("Domain cannot be null when DOMAIN_VERIFICATION_REQUIRED is enabled.")
    elif DOMAIN is None:
        print("Warning: DOMAIN is not set. Please configure DOMAIN before deploying to production.")
    if DOMAIN not in data.get('hd'):
        return False
    if not data.get('email_verified', False):
        return False
    return True


def home_page_user():
    encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
    try:
        decoded_jwt = jwt.decode(encoded_jwt, current_app.secret_key, algorithms=[algorithm, ])
        print(decoded_jwt)
    except Exception as e:
        return Response(
            response=json.dumps({"message": "Decoding JWT Failed", "exception": e.args}),
            status=500,
            mimetype='application/json'
        )
    return Response(
        response=json.dumps(decoded_jwt),
        status=200,
        mimetype='application/json'
    )


def get_login_info(token: str, credentials: bool = True):
    user = models.user.User.get_if_exists(models.user.User.token == token)
    default_project = models.AssetSettings.default_project()
    asset_dashboard_settings = models.AssetSettings.get_if_exists(models.AssetSettings.name == "dashboard_settings")
    if user:
        login_info = {
            "user": {
                "id": str(user.id),
                "username": str(user.username),
                "email": str(user.email),
                "token": user.token,
            },
            "roles": user.get_roles(credentials=credentials),
            "default_project": str(default_project.id) if default_project else None,
            "redirect_url": "/projects",
            "dashboard_settings": json.loads(asset_dashboard_settings.value) if asset_dashboard_settings else None
        }
    else:
        login_info = {
            "error": "invalid user"
        }
    return login_info
