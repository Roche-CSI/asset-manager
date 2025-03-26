import logging

from asset_utils.common import exceptions
from flask import Blueprint, Response, request

from server_core.models.asset import Asset
from server_core.models.asset_class import AssetClass
from server_core.utils.json_encoder import to_json
from server_core.views.utils.asset_updater import update_asset_record
from server_core.views.utils.view_utils import data_from_request

logger = logging.getLogger(__file__)

asset_view = Blueprint(name='asset_view', import_name=__name__)


@asset_view.route('', methods=['GET', 'POST'])
def list_assets():
    if request.method == 'GET':
        result = get_assets(args=request.args)
    else:
        # create node
        result = create_asset_record(**data_from_request(request)).to_dict()
    return Response(to_json(result), mimetype="application/json", status=200)


@asset_view.route('/<id>', methods=['GET', 'PUT'])
def get_asset(id: str):
    asset = Asset.get_if_exists(Asset.id == id)
    if not asset:
        return Response(to_json({"error": f"asset with id:{id} not found"}), mimetype="application/json", status=404)

    result = asset.to_dict()
    if request.method == "PUT":
        data = data_from_request(request)
        try:
            result = update_asset_record(asset=asset, data=data)
        except Exception as e:
            logger.exception("Error occurred while updating the asset.")
            # append the error message to the status so response.raise_for_status() can get it
            if isinstance(e, exceptions.AssetException):
                return Response(to_json({"error": e.msg}), mimetype="application/json", status=f"500 {e.msg}")
            return Response(to_json({"error": str(e)}), mimetype="application/json", status=f"500 {e}")

    return Response(to_json(result), mimetype="application/json", status=200)


def get_assets(args: dict):
    if not args:
        return [node for node in Asset.public().dicts()]

    # client will ask if refs are valid before committing
    # we check and return the assets here
    if args.get("asset_name"):
        asset = retrieve_asset_with_name(asset_name=args.get("asset_name"))
        if args.get("name"):
            # user needs name only
            return asset.leaf_version().name
        else:
            return asset.to_dict()

    elif args.get("alias") and args.get("class_name"):
        asset = retrieve_asset_with_alias(
            class_name=args.get("class_name"),
            alias=args.get("alias"))
        if not asset:
            return None
        if args.get("name"):
            # user ask for name only
            return asset.leaf_version().name
        else:
            return asset.to_dict()
    else:
        return None


def retrieve_asset_with_name(asset_name):
    class_name, seq_id = asset_name.split("/")
    class_id = AssetClass.get_if_exists(AssetClass.name == class_name)
    if class_id:
        return Asset.get_if_exists(Asset.asset_class == class_id, Asset.seq_id == seq_id)
    else:
        return None


def retrieve_asset_with_alias(class_name, alias):
    class_id = AssetClass.get_if_exists(AssetClass.name == class_name)
    if class_id:
        return Asset.get_if_exists(Asset.asset_class == class_id, Asset.alias == alias)
    else:
        return None


def create_asset_record(**kwargs):
    """Inserts a new row in the Asset table
    Parameters
    ----------
    kwargs

    Returns
    -------
    """
    asset = Asset.create(user=kwargs.pop("user"),
                         asset_class=kwargs.pop("class_id"),
                         parent=kwargs.pop("parent"),
                         **kwargs
                         )
    return asset
