import json

from flask import Blueprint, Response, request

from server_core import models
from server_core.utils.json_encoder import to_json
from server_core.views.auth_views import auth_utils

view = Blueprint(name='cli_auth_view', import_name=__name__)


@view.route('/signup', methods=['POST'])
def signup():
    data: dict = json.loads(request.data.decode("utf-8"))
    return Response(to_json(auth_utils.user_signup(data=data)), status=201)


@view.route('/google_auth', methods=['GET'])
def google_auth():
    auth: models.AuthProvider = models.AuthProvider.get(models.AuthProvider.name == "google_auth")
    return to_json(auth.configs)


@view.route('/google_auth_url', methods=['GET'])
def google_auth_url():
    flow, _ = auth_utils.get_flow()
    authorization_url, _ = flow.authorization_url()
    return to_json(authorization_url)


@view.route('/response_login', methods=['POST'])
def response_login():
    data = json.loads(request.data.decode("utf-8"))  # ascii doesn't work for readme
    flow, configs = auth_utils.get_flow(redirect_uri=data.get("redirect_uri"))
    flow.fetch_token(authorization_response=data.get("response"))
    client_id = configs.get("web").get("client_id")

    return login_response(client_id=client_id, token=flow.credentials.id_token)


@view.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data.decode("utf-8"))  # ascii doesn't work for readme
    return login_response(client_id=data.get("client_id"), token=data.get("id_token"))


@view.route('/token_login', methods=['POST'])
def token_login():
    data: dict = json.loads(request.data.decode("utf-8"))  # ascii doesn't work for readme
    login_info: dict = auth_utils.get_login_info(token=data.get("token"), credentials=True)
    return Response(
        response=json.dumps(login_info),
        status=200,
        mimetype='application/json'
    )


def login_response(client_id: str, token: str) -> Response:
    """Validate the user data and return the login response."""
    user_info = auth_utils.verify_oauth2_token(client_id=client_id, token=token)
    if auth_utils.validate_user_data(data=user_info):
        # check if record exists
        user = models.user.User.get_if_exists(models.user.User.email == user_info.get("email"))
        default_project = models.AssetSettings.default_project()
        if user:
            login_info = {
                "user": {
                    "id": str(user.id),
                    "username": str(user.username),
                    "email": str(user.email)
                }
            }
            jwt_token = auth_utils.generate_jwt(login_info)
            user.g_info = user_info
            user.token = jwt_token
            user.save(user=user.username)
            login_info["roles"] = user.get_roles()
            login_info["user"]["token"] = jwt_token
            login_info["default_project"] = str(default_project.id) if default_project else None
        else:
            login_info = {
                "error": {
                    "type": "invalid user",
                    "value": f"user with {user_info.get('email')} doesn't exist"
                }
            }
    else:
        login_info = {
            "error": {
                "type": "invalid email",
                "value": f"{user_info.get('email')} is not a valid email, "
                         f"you must use a valid email to signup"
            }
        }

    return Response(
        response=json.dumps(login_info),
        status=200,
        mimetype='application/json'
    )
