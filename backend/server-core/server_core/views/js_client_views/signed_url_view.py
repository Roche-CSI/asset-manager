import logging

from flask import Blueprint, Response, request

from server_core.models.object import Object as ObjectModel
from server_core.utils import json_encoder
from server_core.views.utils import signed_url_for_content

logger = logging.getLogger(__file__)

url_view = Blueprint(name='gcs_url_view', import_name=__name__)


@url_view.route('', methods=['GET'])
def get_signed_url():
    class_id, object_id = request.args.get("class_id"), request.args.get("object_id")
    object_record = ObjectModel.get_if_exists(ObjectModel.id == object_id)
    if not object_record:
        result = {
            "error": "object not found"
        }
    else:
        signed_url = signed_url_for_content(content=object_record.content, class_id=class_id)
        if not signed_url:
            result = {
                "error": "object not downloadable",
                "object": object_record.to_dict(recurse=True)
            }
        else:
            result = {"signed_url": signed_url, "object": object_record.to_dict(recurse=True)}

    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)
