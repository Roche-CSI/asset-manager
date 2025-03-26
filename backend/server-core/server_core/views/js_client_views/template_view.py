import logging

from flask import Blueprint, Response, request
from peewee import DoesNotExist

from server_core.models.template import Template
from server_core.utils import json_encoder
from server_core.views.utils import view_utils

logger = logging.getLogger(__file__)

view = Blueprint(name='db_template_view', import_name=__name__)


@view.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return get_templates()
    elif request.method == "POST":
        return create_template()


def get_templates():
    """Returns a list of get_projects based on query params"""
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    result = [record.to_dict() for record in Template.public()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)


@view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    proj = Template.get_or_none(Template.id == id)
    if not proj:
        return Response(json_encoder.to_json({}), mimetype="application/json", status=404)
    return Response(json_encoder.to_json(proj.to_dict()), mimetype="application/json", status=200)


def create_template():
    # create project
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("missing required param: user")

    name = data.get("name")
    version = data.get("version")
    try:
        _ = Template.get(Template.name == name, Template.version == version)
        result = {"error": "template already exists with name:{} and version:{}".format(name, version)}
        res_code = 400
    except DoesNotExist as e:
        logger.info("bucket not found, creating a new record with url:{}".format(bucket_url))
        created = Template.create(user=user,
                                  name=name,
                                  version=version,
                                  description=data.get("description"),
                                  readme=data.get("readme"),
                                  is_active=data.get(True))

        result = created.to_dict()
        res_code = 201  # created
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


@view.route('/<id>', methods=['PUT'])
def update_template(id: str):
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("missing required param: user")
    try:
        existing = Template.get(Template.id == id)
        for field in data:
            setattr(existing, field, data[field])
        existing.save(user=user)
        result = existing.to_dict()
        res_code = 200
    except DoesNotExist as e:
        logger.info("template not found")
        res_code = 404  # not found
        result = {}
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
