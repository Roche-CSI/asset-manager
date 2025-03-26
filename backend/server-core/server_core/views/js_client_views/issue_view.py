import logging

from flask import Blueprint, Response, request

from server_core.models import AppSecret, AssetSettings
from server_core.utils import json_encoder
from server_core.views.utils import view_utils
from server_core.views.utils.async_post import post_to_url

logger = logging.getLogger(__file__)

issue_view = Blueprint(name='issue_view', import_name=__name__)


@issue_view.route('', methods=['POST'])
def create_github_issue():
    """
    Create a github issue
    Uses a github token in the app secrets table with the name "github_token"
    Uses a github_url in the asset settings table with the name "github_url"
    """
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("missing required param: user")

    url = AssetSettings.get(AssetSettings.name == "github_url").value + "/issues"
    github_secret = AppSecret.get(AppSecret.name == "github_token")

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + github_secret.secret,
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {'title': data.get("title"),
            'body': data.get("description"),
            'labels': ['bug']}

    post_to_url(url, data, headers)

    res_code = 201  # created
    return Response(json_encoder.to_json("Successfully created issue"), mimetype="application/json", status=res_code)
