import json
import logging

from flask import Blueprint, Response, request
from peewee import DoesNotExist

from server_core.models import AssetClass, Project
from server_core.utils.json_encoder import to_json
from server_core.views.utils import view_utils

logger = logging.getLogger(__file__)

asset_class_view = Blueprint(name='db_asset_class_view', import_name=__name__)


@asset_class_view.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return list_classes()
    elif request.method == "POST":
        return create_asset_class()


def create_asset_class():
    # create asset_class
    data: dict = view_utils.data_from_request(request)
    class_name = data.get("name")

    if not data.get("project_id"):
        raise Exception("missing required param: project_id")

    project = Project.get(Project.id == data.get("project_id"))
    try:
        existing: AssetClass = AssetClass.get(AssetClass.name == class_name, AssetClass.project == project.id)
        result = existing.to_dict()
        res_code = 200
    except DoesNotExist as e:
        logger.info("asset_class not found, creating a new record with name:{}".format(class_name))
        created: AssetClass = AssetClass.create(user=data.get("user"),
                                                name=class_name,
                                                title=data.get("title"),
                                                class_type=data.get("class_type"),
                                                description=data.get("description"),
                                                readme=data.get("readme"),
                                                project_id=data.get("project_id"))
        # write to bucket
        created.write_to_bucket()
        result = created.to_dict()
        res_code = 201  # created
    return Response(to_json(result), mimetype="application/json", status=res_code)


def list_classes():
    args = request.args
    result = []
    project_id = args.get("project")
    if not project_id:
        raise Exception("missing required param: project_id")
    if args.get("class_names"):
        class_names = args.getlist("class_names")
        for name in class_names:
            asset_class = AssetClass.get_or_none(AssetClass.project == project_id, AssetClass.name == name)
            if asset_class:
                result.append(asset_class.to_dict())
    elif args.get("project"):
        result = [asset_cls.to_dict() for asset_cls in
                  AssetClass.select().where(AssetClass.project == args.get("project"))]
    else:
        result = [asset for asset in AssetClass.select().dicts()]

    return Response(to_json(result), mimetype="application/json", status=200)


@asset_class_view.route('/<id>', methods=['GET', 'PUT'])
def get_put(id: str):
    if request.method == 'GET':
        return get_asset_class(id)
    elif request.method == 'PUT':
        return update_asset_class(id)


def get_asset_class(id: str):
    asset_cls = AssetClass.get(AssetClass.id == id)
    return Response(to_json(asset_cls.to_dict()), mimetype="application/json", status=200)


def update_asset_class(id):
    data: dict = json.loads(request.data.decode("utf-8"))  # ascii doesn't work for readme
    user = data.pop("user")
    if not user:
        raise Exception("missing required param: user")
    try:
        existing: AssetClass = AssetClass.get(AssetClass.id == id)
        for field in data:
            setattr(existing, field, data[field])
        existing.save(user=user)
        existing.write_to_bucket()
        result = existing.to_dict()
        res_code = 200
    except DoesNotExist as e:
        logger.info("asset_class not found")
        # write to bucket
        res_code = 404  # not found
        result = {}
    return Response(to_json(result), mimetype="application/json", status=res_code)
