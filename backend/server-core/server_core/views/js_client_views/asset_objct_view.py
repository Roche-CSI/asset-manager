import logging

from flask import Blueprint, Response, request

from server_core.models import asset, object as asset_object
from server_core.utils import json_encoder

logger = logging.getLogger(__file__)

asset_object_view = Blueprint(name='db_asset_object_view', import_name=__name__)


@asset_object_view.route('', methods=['GET'])
def list_objects():
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    return Response(json_encoder.to_json(get_objects(args=request.args)), mimetype="application/json", status=200)


def get_objects(args: dict):
    """Returns a list of asset_objects based on query params"""
    if args.get("asset_id"):
        asset_record = asset.Asset.get_if_exists(asset.Asset.id == args.get("asset_id"))
        if asset_record:
            return [obj.to_dict() for obj in asset_record.all_objects()]
        else:
            return []
    return [obj.to_dict() for obj in asset_object.Object.public()]


@asset_object_view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    obj = asset_object.Object.get(asset_object.Object.id == id)
    return Response(json_encoder.to_json(obj.to_dict()), mimetype="application/json", status=200)
