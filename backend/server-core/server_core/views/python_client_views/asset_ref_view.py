import logging

from flask import Blueprint, Response, request
from werkzeug.datastructures import ImmutableMultiDict

from server_core.asset_client.exceptions import AssetException
from server_core.models import asset_ref
from server_core.models.asset_ref import AssetRef
from server_core.models.asset_version import AssetVersion
from server_core.utils import json_encoder
from server_core.views.utils.view_utils import data_from_request

logger = logging.getLogger(__file__)

asset_ref_view = Blueprint(name='asset_ref_view', import_name=__name__)


@asset_ref_view.route('', methods=['GET', 'POST'])
def list():
    data: dict = data_from_request(request)
    user = data.get('user')
    if not user:
        raise Exception("required param missing: user")

    if request.method == 'GET':
        res_code = 200
        asset_name = data.get('asset_name')
        if asset_name:
            result = AssetRef.find(project_id=request.args.get("project_id"), name=asset_name)
        else:
            result = [ref.to_dict() for ref in asset_ref.AssetRef.public()]
    else:
        # create or remove refs
        try:
            result = create_remove_refs(user=user, data=data)
            result = [ref.to_dict() for ref in result]
            res_code = 201  # created
        except AssetException as e:
            res_code = 500  # server error
            result = e.to_json()

    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


def create_remove_refs(user, data: dict) -> [AssetRef]:
    """
    Parameters
    ----------
    user
    data: dict
        {added: [{'name': <asset_name>, 'id': <version_id>}], removed: []}
    Returns
    -------
    list:
        list of refs for the asset version
    """
    # add/remove refs
    to_add = data.get('added', [])
    to_remove = data.get('removed', [])
    created = []
    target_ver: AssetVersion = None
    for ref in to_add:
        if not target_ver or target_ver.id != ref.get('dst_version'):
            target_ver = AssetVersion.get(AssetVersion.id == ref.get('dst_version'))
        if target_ver.can_add_refs():
            created.append(AssetRef.create_if_not_exists(user=user,
                                                         src_version=ref.get('src_version'),
                                                         dst_version=target_ver.id,
                                                         label=ref.get('label'),
                                                         properties=ref.get('properties')
                                                         ))
        else:
            msg = f"unable to create ref to target version: {target_ver.name}, this is not a root version"
            raise AssetException(msg=msg)
    deleted = []
    for ref in to_remove:
        if not target_ver or target_ver.id != ref.get('dst_version'):
            target_ver = AssetVersion.get(AssetVersion.id == ref.get('dst_version'))
        ref_record = AssetRef.get_if_exists(AssetRef.id == ref.get('id'))  # always delete with id
        if ref_record:
            ref_record.delete_instance(user=user)
            # ref_record.delete(user=user)
            # TODO: clean up this function
        deleted.append(ref_record)

    # return the final list of refs
    return AssetRef.public().where(AssetRef.dst_version == target_ver) if target_ver else []

    # # the destination versions are same for all to_add and to_remove
    # # because from the client side, upload happens version wise
    # target = None
    # if to_add:
    #     target = to_add[0].get('dst_version')
    # elif to_remove:
    #     target = to_remove[0].get('dst_version')
    # if target:
    #     return AssetRef.public().where(AssetRef.dst_version == target)
    # else:
    #     return []
    #
    #
    # version = AssetVersion.get(AssetVersion.id == dst)
    # if version.can_add_refs():
    #     ref_records = AssetRef.create_refs(user=user,
    #                                        sources=[ref.get("id") for ref in refs],
    #                                        dst=version.id)
    # else:
    #     raise Exception("invalid operation")
    # return ref_records


@asset_ref_view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    version = asset_ref.AssetRef.get(asset_ref.AssetRef.id == id)
    return Response(json_encoder.to_json(version.to_dict()), mimetype="application/json", status=200)


@asset_ref_view.route('/find', methods=['GET'])
def find():
    data: dict = data_from_request(request)
    user = data.get('user')
    if not user:
        raise Exception("required param missing: user")
    return Response(json_encoder.to_json(find_refs(request.args)), mimetype="application/json", status=200)


def find_refs(args: ImmutableMultiDict) -> dict:
    # find version_ids
    results = {}
    asset_names = args.getlist('asset_name')
    for asset_name in asset_names:
        # refs are asset names
        refs = asset_ref.AssetRef.find(project_id=args.get("project_ud"), name=asset_name)
        results[asset_name] = refs
    return results
