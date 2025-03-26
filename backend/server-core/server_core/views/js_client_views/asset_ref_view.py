import logging

from flask import Blueprint, Response, request
from werkzeug.datastructures import ImmutableMultiDict

from server_core.models import asset_ref
from server_core.models.asset import Asset
from server_core.models.asset_ref import AssetRef
from server_core.models.asset_version import AssetVersion
from server_core.utils import json_encoder

logger = logging.getLogger(__file__)

asset_ref_view = Blueprint(name='db_asset_ref_view', import_name=__name__)


@asset_ref_view.route('', methods=['GET'])
def list():
    res_code = 200
    asset_name = request.args.get('asset_name')
    if asset_name:
        result = AssetRef.find(project_id=request.args.get("project_id"),
                               name=asset_name)
    else:
        result = [ref.to_dict() for ref in asset_ref.AssetRef.public()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


@asset_ref_view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    version = asset_ref.AssetRef.get(asset_ref.AssetRef.id == id)
    return Response(json_encoder.to_json(version.to_dict()), mimetype="application/json", status=200)


@asset_ref_view.route('/find', methods=['GET'])
def find():
    args = request.args
    if not args.get('user'):
        raise Exception("required param missing: user")
    return Response(json_encoder.to_json(find_refs(request.args)), mimetype="application/json", status=200)


def find_refs(args: ImmutableMultiDict) -> dict:
    # find version_ids
    asset_names = args.getlist('asset_name')
    version_numbers = args.getlist("version_number")

    version = version_numbers[0] if version_numbers else None
    asset = asset_names[0] if asset_names else None

    result = {}
    if asset:
        result[asset] = {}
        if version:
            # fetch for the version
            result[asset][version] = AssetRef.find(project_id=args.get("project_id"),
                                                   name=AssetVersion.get_name(asset_name=asset, version_number=version))
        else:
            # find for all versions of the asset
            asset_record = Asset.find_by_name(asset_name=asset)
            for version in asset_record.get_versions():
                result[asset][version.number] = AssetRef.find(args.get("project_id"),
                                                              name=AssetVersion.get_name(asset_name=asset,
                                                                                         version_number=version.number),
                                                              instance=version)

    return result
