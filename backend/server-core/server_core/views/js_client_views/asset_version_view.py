import logging

from flask import Blueprint, Response, request
from werkzeug.datastructures import ImmutableMultiDict

from server_core.models import asset_version
from server_core.utils import json_encoder

logger = logging.getLogger(__file__)

asset_version_view = Blueprint(name='dashboard_asset_version_view', import_name=__name__)


@asset_version_view.route('', methods=['GET'])
def list():
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    # result = [version for version in asset_version.AssetVersion.public().dicts()]
    return Response(json_encoder.to_json(get_versions(args=request.args)), mimetype="application/json", status=200)


def get_versions(args: dict):
    """Returns a list of versions based on query params"""
    if args.get("class_name") or args.get("commit_hash"):
        versions = asset_version.AssetVersion.find_with_hash(
            project_id=args.get("project_id", None),
            class_name=args.get("class_name", None),
            commit_hash=args.get("commit_hash", None)
        )
        return [version.name if args.get("name") else version.to_dict(recurse=True) for version in versions]
    if request.args.getlist("version_names"):
        return find_versions_with_names(args=args)
    if args.get("asset_id"):
        if args.get("number"):
            query = asset_version.AssetVersion.select().where(
                (asset_version.AssetVersion.asset == args.get("asset_id")) &
                (asset_version.AssetVersion.number == args.get("number"))
            )
        else:
            query = asset_version.AssetVersion.select().where(
                (asset_version.AssetVersion.asset == args.get("asset_id"))
            )
        return [version.to_dict() for version in query]

    return [version for version in asset_version.AssetVersion.public().dicts()]


@asset_version_view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    version = asset_version.AssetVersion.get(asset_version.AssetVersion.id == id)
    return Response(json_encoder.to_json(version.to_dict()), mimetype="application/json", status=200)


@asset_version_view.route('/find', methods=['GET'])
def find():
    args = request.args
    if not args.get('user'):
        raise Exception("required param missing: user")
    return Response(json_encoder.to_json(find_versions_with_names(request.args)), mimetype="application/json",
                    status=200)


def find_versions_with_names(args: ImmutableMultiDict) -> dict:
    # find version_ids
    results = {}
    version_names = args.getlist('version_names')
    for ver_name in version_names:
        # refs are asset names
        version = asset_version.AssetVersion.find(name=ver_name)
        if version:
            results[ver_name] = version.to_dict()

    return results
