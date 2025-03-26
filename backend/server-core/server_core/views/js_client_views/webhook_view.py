import json
import logging

from flask import Blueprint, Response, request
from peewee import DoesNotExist

from server_core.models import Webhook
from server_core.utils import json_encoder
from server_core.views.utils import view_utils

logger = logging.getLogger(__file__)

view = Blueprint(name='db_webhook_view', import_name=__name__)


@view.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return get_webhooks()
    elif request.method == "POST":
        return create_webhook()


def get_webhooks():
    """Returns a list of get_projects based on query params"""
    user = request.args.get('user')
    if not user:
        return Response(
            json_encoder.to_json(
                {"error": "missing required param: user"}),
            mimetype="application/json",
            status=400)

    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id')
    if entity_id and entity_type:
        result = [record.to_dict() for record in Webhook.public().where(Webhook.entity_type == entity_type,
                                                                        Webhook.entity_id == entity_id)]
    else:
        result = [record.to_dict() for record in Webhook.public()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)


@view.route('/<id>', methods=['GET'])
def get(id: str):
    user = request.args.get('user')
    if not user:
        return Response(
            json_encoder.to_json(
                {"error": "missing required param: user"}),
            mimetype="application/json",
            status=400)

    hook = Webhook.get_if_exists(Webhook.id == id)
    if not hook:
        return Response(json_encoder.to_json({}), mimetype="application/json", status=404)
    return Response(json_encoder.to_json(hook.to_dict()), mimetype="application/json", status=200)


def create_webhook():
    # create project
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        return Response(
            json_encoder.to_json(
                {"error": "missing required param: user"}),
            mimetype="application/json",
            status=400)

    try:
        hook = Webhook.get(
            Webhook.entity_type == data.get("entity_type"),
            Webhook.entity_id == data.get("entity_id"),
            Webhook.event_type == data.get("event_type"),
            Webhook.event_source == data.get("event_source")
        )
        result = {"error": "template already exists with data: {}".format(json.dumps(hook.to_dict()))}
        res_code = 400
    except DoesNotExist as e:
        logger.info("webhook not found, creating a new record with name:{}".format(data.get("name")))
        created = Webhook.create(user=user, **data)
        result = created.to_dict()
        res_code = 201  # created
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


@view.route('/<id>', methods=['PUT'])
def update_webhook(id: str):
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        return Response(
            json_encoder.to_json(
                {"error": "missing required param: user"}),
            mimetype="application/json",
            status=400)

    try:
        existing = Webhook.get(Webhook.id == id)
        for field in data:
            setattr(existing, field, data[field])
        existing.save(user=user)
        result = existing.to_dict()
        res_code = 200
    except DoesNotExist as e:
        logger.info("webhook not found")
        res_code = 404  # not found
        result = {"error": str(e)}
    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)


@view.route('/<id>', methods=['DELETE'])
def delete_webhook(id: str):
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        return Response(
            json_encoder.to_json({"error": "missing required param: user"}),
            mimetype="application/json",
            status=400)

    try:
        existing = Webhook.get(Webhook.id == id)
        existing.delete_instance(user=user, permanently=True)
        result = existing.to_dict()
        res_code = 200

    except DoesNotExist as e:
        logger.info("webhook not found")
        res_code = 404  # not found
        result = {"error": str(e)}

    return Response(json_encoder.to_json(result), mimetype="application/json", status=res_code)
