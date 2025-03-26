import json
import logging

from flask import Blueprint, Response, request

from server_core.utils.json_encoder import to_json
from server_core.views.utils.view_utils import data_from_request

logger = logging.getLogger(__file__)

view = Blueprint(name='tag_view', import_name=__name__)


@view.route('/validation', methods=['GET'])
def validation():
    data: dict = data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("required param missing: user")
    tags: dict = json.loads(request.args.get("tags"))
    try:
        validated = validate_tags(tags)
    except Exception as e:
        return Response(to_json({"error": str(e)}), mimetype="application/json", status=400)
    return Response(to_json({"validated": validated}), mimetype="application/json", status=200)


def validate_tags(tags: dict):
    """Validate tags dict"""
    for tag_name, tag_value in tags.items():
        if not tag_name or not tag_value:
            raise Exception(f'tag_name and tag_value cannot be empty: {tag_name, tag_value}')
        if ' ' in tag_name:
            raise Exception(f'tag_name cannot contain spaces: {tag_name}')
    return True
