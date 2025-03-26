import logging

from flask import Blueprint, Response, request

from server_core.models import asset_settings
from server_core.utils import json_encoder

logger = logging.getLogger(__file__)

view = Blueprint(name='db_asset_settings_view', import_name=__name__)


@view.route('', methods=['GET'])
def list():
    res_code = 200
    record_name = request.args.get('name')
    if record_name:
        result = asset_settings.AssetSettings.get_if_exists(asset_settings.AssetSettings.name == record_name)
        result = result.to_dict() if result else {}
    else:
        result = [record.to_dict() for record in asset_settings.AssetSettings.public()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
