import json
import logging

from asset_pluggy.storage import BlobStoreURL
from asset_plugin_gcs.bucket_cors import update_cors_configuration as gcs_update_cors
from asset_plugin_s3.bucket_cors import set_bucket_cors as s3_update_cors
from flask import Blueprint, Response, request
from peewee import DoesNotExist

from server_core.configs import Configs
from server_core.models.bucket import Bucket
from server_core.utils import json_encoder
from server_core.views.utils import view_utils

logger = logging.getLogger(__file__)

view = Blueprint(name='db_bucket_view', import_name=__name__)


@view.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return get_buckets()
    elif request.method == "POST":
        return create_bucket()


def get_buckets():
    """Returns a list of get_projects based on query params"""
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    result = [record.to_dict() for record in Bucket.public()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)


@view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    proj = Bucket.get_or_none(Bucket.id == id)
    if not proj:
        return Response(json_encoder.to_json({}), mimetype="application/json", status=404)
    return Response(json_encoder.to_json(proj.to_dict()), mimetype="application/json", status=200)


def create_bucket():
    # create project
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("missing required param: user")

    bucket_url = data.get("bucket_url")
    try:
        existing = Bucket.get(Bucket.bucket_url == bucket_url)
        result = existing.to_dict()
        res_code = 200
    except DoesNotExist as e:
        logger.info("bucket not found, creating a new record with url:{}".format(bucket_url))
        created = Bucket.create(user=user,
                                url=bucket_url,
                                keys=data.get("keys"),
                                description=data.get("description"),
                                is_active=data.get(True))

        # write to bucket and set cors
        try:
            cors_url = update_cors(data)
            created.cors_config = {"cors_urls": [cors_url]}
            created.save(user=user)
        except Exception as e:
            logger.error("error writing to bucket or update bucket cors: {}".format(e))
            res_code = 400
            configs = created.cors_config or {}
            configs["cors_error"] = "error in setting cors configurations: {}".format(e)
            created.cors_config = configs
            created.save(user=user)
            return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
        result = created.to_dict()
        res_code = 201  # created
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


def update_cors(data: dict):
    store_url = BlobStoreURL(url=data.get("bucket_url"))
    update_by_host_name = {"s3": s3_update_cors, "gs": gcs_update_cors}
    host = store_url.host
    host_update_cors = update_by_host_name[host]
    cors_url = Configs.shared().frontend_url
    host_update_cors(credentials=json.loads(data.get("keys")),
                     bucket_name=store_url.bucket,
                     origin_url=cors_url)
    return cors_url


@view.route('/<id>', methods=['PUT'])
def update_bucket(id: str):
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("missing required param: user")
    try:
        existing = Bucket.get(Bucket.id == id)
        for field in data:
            setattr(existing, field, data[field])
        existing.save(user=user)
        result = existing.to_dict()
        res_code = 200
    except DoesNotExist as e:
        logger.info("bucket not found")
        res_code = 404  # not found
        result = {}
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
