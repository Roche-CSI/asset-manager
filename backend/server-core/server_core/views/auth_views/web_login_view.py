import json
import os
import jwt
from urllib.parse import unquote
from flask import Blueprint, Response, request, make_response, current_app
from flask.globals import session
from werkzeug.utils import redirect

from server_core import models
from server_core.configs import Configs
from server_core.utils.json_encoder import to_json
from server_core.views.auth_views import auth_utils
from server_core.views.utils import view_utils

# bypass http
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

view = Blueprint(name='auth_view', import_name=__name__)


@view.route("", methods=['GET'])
def index():
    return "works"


@view.route("/signup", methods=["POST"])
def signup():
    data: dict = json.loads(request.form.get("data") or request.data.decode("utf-8"))
    return Response(to_json(auth_utils.user_signup(data=data)), status=201)


@view.route("/login", methods=['GET'])
def login():
    """
    This function starts the OAuth2 authorization process by generating an
    authorization URL and storing the necessary state information in the
    session.
    1. Extracts the `client_url` from the request arguments by the client, used
       to redirect the user back to the client application in the callback phase later.
    2. Constructs the server redirect URI for the OAuth2 callback endpoint.
    3. Initializes the OAuth2 flow and generates the authorization URL and state.
    Returns:
        A Flask `Response` object containing a JSON payload with the
        `authorization_url` to redirect the user to the OAuth2 provider for
        authentication.
    """
    args = request.args
    client_url = args.get("client_url")
    redirect_uri = Configs.shared().host_url + "/auth/web/callback"
    flow, configs = auth_utils.get_flow(redirect_uri=redirect_uri)
    authorization_url, state = flow.authorization_url()
    # Store the state so the callback can verify the auth server response.
    session["state"] = state
    session["client_url"] = client_url
    return Response(
        response=json.dumps({'auth_url': authorization_url}),
        status=200,
        mimetype='application/json'
    )


@view.route("/callback")
def callback():
    """
    This function is triggered when the user is redirected back from the
    OAuth2 provider after authentication. It completes the OAuth2 flow by
    fetching the access token, verifying the ID token.
    Returns:
        A Flask `Response` object that redirects the user to the client_url
        application URL with a JWT token set as a cookie.

    Note: jwt cookie should be set secure=True for production, False for dev
    """
    redirect_uri = Configs.shared().host_url + "/auth/web/callback"
    flow, configs = auth_utils.get_flow(redirect_uri=redirect_uri)
    client_id = configs["web"]["client_id"]
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    id_info = auth_utils.verify_oauth2_token(token=credentials._id_token,
                                             client_id=client_id
                                             )
    session["google_id"] = id_info.get("sub")

    # removing the specific audience, as it is throwing error
    # insert into user table
    user = None
    if auth_utils.validate_user_data(data=id_info):
        # check if record exists
        user = models.user.User.get_if_exists(models.user.User.email == id_info.get("email"))
        if user:
            login_info = {
                "user": {
                    "id": str(user.id),
                    "username": str(user.username),
                    "email": str(user.email)
                }
            }
            jwt_token = auth_utils.generate_jwt(login_info)
            user.g_info = id_info
            user.token = jwt_token
            user.save(user=user.username)
        else:
            login_info = {
                "error": "invalid user"
            }
    else:
        login_info = {
            "error": f"invalid email: {id_info.get('email')}"
        }

    jwt_token = auth_utils.generate_jwt(login_info)
    DEFAULT_FRONTEND_URL = Configs.shared().frontend_url
    client_url = session.get("client_url", DEFAULT_FRONTEND_URL)
    decoded_client_url = unquote(client_url)
    # print("decoded_client_url", decoded_client_url)
    response = make_response(redirect(f"{decoded_client_url}"))
    response.set_cookie('jwt', jwt_token, httponly=True, secure=True, samesite=None)
    return response

    """ return Response(
        response=json.dumps({'JWT':jwt_token}),
        status=200,
        mimetype='application/json'
    ) """


@view.route("/token_refresh", methods=['POST'])
def refresh():
    data: dict = json.loads(request.form.get("data") or request.data.decode("ascii"))
    token = data.get('token')
    response = auth_utils.validate_and_refresh_jwt(token)
    return response


@view.route("/token_validate", methods=['GET'])
def validate():
    username = request.args.get('username')
    email = request.args.get('email')
    token = request.args.get('token')
    existing = models.user.User.get_if_exists(models.user.User.username == username,
                                              models.user.User.email == email,
                                              models.user.User.token == token)
    if not existing:
        return Response(
            response=json.dumps(False),
            status=500,
            mimetype='application/json'
        )
    return Response(
        response=json.dumps(True),
        status=200,
        mimetype='application/json'
    )


@view.route("/logout")
def logout():
    # clear the local storage from frontend
    session.clear()
    return Response(
        response=json.dumps({"message": "Logged out"}),
        status=202,
        mimetype='application/json'
    )


@view.route('/token_login', methods=['POST'])
def token_login():
    """
    Authenticate a user and return user info using a JWT token.
    Retrieves the JWT token from the request arguments or cookies.
    If the request comes from CLI to the client and to the server, retrieves from args
    and also set cookies in response
    If the request comes from the client to the server, retrieves from cookies
    Returns:
        A Flask `Response` object containing a JSON payload with either the
        user's information or an error message. The response status code
        indicates success (200) or failure (401 or 500).
    Note: jwt cookie should be set secure=True for production, False for dev
    """
    request_data: dict = view_utils.data_from_request(request)
    jwt_token: str = request_data.get('jwt') or request.cookies.get('jwt')
    status_code = 200
    if not jwt_token:
        response_data = {"error": "No token provided"}
        status_code = 401
    else:
        try:
            decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            login_info = auth_utils.get_login_info(token=jwt_token, credentials=False)
            response_data = login_info
        except Exception as e:
            response_data = {"error": "Failed decoding user token"}
            status_code = 500
    response = make_response(json.dumps(response_data), status_code)
    from_cli = bool(request_data.get('jwt'))
    if from_cli:
        response.set_cookie('jwt', jwt_token, httponly=True, secure=True, samesite=None)
    return response
