import logging

from flask import Blueprint, Response, request

from server_core import models
from server_core.utils.json_encoder import to_json

logger = logging.getLogger(__file__)

view = Blueprint(name='project_view', import_name=__name__)


@view.route('', methods=['GET'])
def index():
    result = [project.to_dict(fields=models.Project.public_fields()) for project in models.Project.public()]
    return Response(to_json(result), mimetype="application/json", status=200)


@view.route('/token', methods=['GET'])
def get_token():
    project_id = request.args.get("project_id")
    project = models.Project.get(models.Project.id == project_id)
    return Response(to_json(project.storage_token()), mimetype="application/json", status=200)
