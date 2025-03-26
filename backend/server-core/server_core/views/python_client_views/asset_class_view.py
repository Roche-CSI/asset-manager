import logging

from flask import Blueprint, Response, request
from peewee import DoesNotExist

from server_core import models
from server_core.models.asset_class import AssetClass
from server_core.utils.json_encoder import to_json
from server_core.views.utils.view_utils import data_from_request

logger = logging.getLogger(__file__)

asset_class_view = Blueprint(name='asset_class_view', import_name=__name__)


@asset_class_view.route('', methods=['GET', 'POST'])
def list_classes():
    res_code = 200  # ok
    if request.method == 'GET':
        result = [asset for asset in AssetClass.public().dicts()]
    else:
        # create asset_class
        data: dict = data_from_request(request)
        class_name, project = data.get("class_name"), data.get("project")
        if not project:
            raise Exception("missing required param: project")
        try:
            class_record = AssetClass.get(name=class_name, project=project)
        except DoesNotExist as e:
            logger.info("asset_class not found, creating a new record with name:{}".format(class_name))
            proj_record: models.Project = models.Project.get(models.Project.id == project)
            with proj_record.storage():
                class_record: AssetClass = AssetClass.create(user=data.get("user"),
                                                             name=class_name,
                                                             project=project)
                class_record.write_to_bucket()
                # write yaml files to bucket
                # result = class_record.to_dict(fields=AssetClass.yaml_fields())
                # yaml_data = [
                #     {
                #         "data": result,
                #         "url": Configs.shared().asset_class_url(class_id=class_record.id)
                #     },
                #     {
                #         "data": {record.name: str(record.id) for record in proj_record.asset_classes},
                #         "url": Configs.shared().class_list_url
                #     }
                # ]
                res_code = 201  # created

                # commit = CommitData()
                # commit.write_to_bucket(storage_url=proj_record.remote_url, data=yaml_data)

    return Response(to_json(class_record.to_dict()), mimetype="application/json", status=res_code)


@asset_class_view.route('/<id>', methods=['GET', 'PUT'])
def get_asset_class(id: str):
    asset_cls = AssetClass.get(AssetClass.id == id)
    if request.method == "PUT":
        data = data_from_request(request)
        # only update allowed is tags, otherwise nodes are immutable
        asset_cls.tags += data.get("tags")
        asset_cls.save(only=[AssetClass.tags])
    return Response(to_json(asset_cls.to_dict()), mimetype="application/json", status=200)
