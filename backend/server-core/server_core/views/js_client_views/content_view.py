import logging

from flask import Blueprint, Response, request
from werkzeug.datastructures import ImmutableMultiDict

from server_core.models import content
from server_core.utils import json_encoder

logger = logging.getLogger(__file__)

content_view = Blueprint(name='db_content_view', import_name=__name__)


@content_view.route('', methods=['GET'])
def list():
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    return Response(json_encoder.to_json(get_contents(args=request.args)), mimetype="application/json", status=200)


def get_contents(args: ImmutableMultiDict):
    """Returns a list of asset_objects based on query params"""
    content_ids = args.get("content_ids")
    result = {}
    if content_ids:
        content_ids = content_ids.split(",")
        for c_id in content_ids:
            record = content.Content.get_if_exists(content.Content.id == c_id)
            if record:
                result[c_id] = record.to_dict()
    else:
        result = [record.to_dict() for record in content.Content.public()]

    return result


@content_view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    record = content.Content.get_if_exists(content.Content.id == id)
    return Response(json_encoder.to_json(record.to_dict()), mimetype="application/json", status=200)
