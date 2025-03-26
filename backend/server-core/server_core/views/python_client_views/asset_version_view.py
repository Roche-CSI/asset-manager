import logging

from flask import Blueprint, Response, request
from werkzeug.datastructures import ImmutableMultiDict, MultiDict

from server_core.models import AssetVersion
from server_core.models.asset import Asset
from server_core.utils import json_encoder
from server_core.views.utils.view_utils import data_from_request

logger = logging.getLogger(__file__)

asset_version_view = Blueprint(name='asset_version_view', import_name=__name__)


# validate either request.args.get('user') or g.user
@asset_version_view.route('', methods=['GET'])
def list_versions():
    data = data_from_request(request)
    user = data.get('user')
    if not user:
        raise Exception("required param missing: user")
    # result = [version for version in asset_version.AssetVersion.public().dicts()]
    return Response(json_encoder.to_json(get_versions(args=request.args)), mimetype="application/json", status=200)


def get_versions(args: dict) -> list:
    """Returns a list of versions based on query params"""
    # user asked for the leaf version
    parsed = cast_dict(args)
    if parsed.get("leaf_version") or parsed.get("version_number"):
        if not parsed.get("project_id"):
            raise Exception("required params missing: project_id")
        if not parsed.get("class_name") and not parsed.get("class_id"):
            raise Exception("required params missing: class_name or class_id")
        asset_record = Asset.find(project_id=parsed.get("project_id"),
                                  class_name=parsed.get("class_name"),
                                  class_id=parsed.get("class_id"),
                                  seq_id=parsed.get("seq_id"))
        if parsed.get("version_number"):
            # retrieve the version record
            version_record = AssetVersion.select().where(
                AssetVersion.asset == asset_record,
                AssetVersion.number == parsed.get("version_number")
            ).get()
        else:
            # get the leaf version
            version_record = asset_record.leaf_version()
        return [version_record.to_dict()]

    if args.get("class_name") or args.get("commit_hash"):
        versions = AssetVersion.find_with_hash(
            project_id=args.get("project_id", None),
            class_name=args.get("class_name", None),
            commit_hash=args.get("commit_hash", None)
        )
        return [version.name if args.get("name") else version.to_dict(recurse=True) for version in versions]
    if request.args.getlist("version_names"):
        return find_versions_with_names(args=args)

    return [version for version in AssetVersion.public().dicts()]


@asset_version_view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    if request.method == "GET":
        version = AssetVersion.get(AssetVersion.id == id)
        return Response(json_encoder.to_json(version.to_dict()), mimetype="application/json", status=200)
    else:
        raise Exception("method not allowed")


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
        version = AssetVersion.find(project_id=args.get("project_id"),
                                    name=ver_name)
        if version:
            results[ver_name] = version.to_dict()

    return results


def cast_dict(d):
    def immutable_multi_dict_to_dict(immutable_multi_dict):
        """Convert ImmutableMultiDict to a standard Python dict."""
        result_dict = {}
        for key, values in immutable_multi_dict.lists():
            # Choose how to handle multiple values:
            # - Store as a list of values
            # - Or store the first value, etc.
            if len(values) > 1:
                result_dict[key] = values
            else:
                result_dict[key] = values[0]
        return result_dict

    def convert_string_to_type(value):
        """Convert specific strings to their actual Python types."""
        if value == 'None':
            return None
        elif value == 'True':
            return True
        elif value == 'False':
            return False
        # Add more conversions as needed
        return value

    if isinstance(d, MultiDict):
        d = immutable_multi_dict_to_dict(d)

    """Recursively convert values in a dictionary."""
    try:
        if isinstance(d, dict):
            return {k: cast_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [cast_dict(i) for i in d]
        else:
            return convert_string_to_type(d)
    except Exception:
        print("Error converting dictionary")
        raise
