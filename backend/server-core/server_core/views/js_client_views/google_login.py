import os

from flask import Blueprint, Response, request, redirect, url_for
import logging
from server_core.utils.json_encoder import to_json
from flask_dance.contrib.google import make_google_blueprint, google

CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")

logger = logging.getLogger(__file__)
google_login_view = make_google_blueprint(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=["profile", "email"],
    offline=True,
    reprompt_consent=True
)
# google_login_view = Blueprint(name='google_login_view', import_name=__name__)


@google_login_view.route("/", methods=["GET"])
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/plus/v1/people/me")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["emails"][0]["value"])
