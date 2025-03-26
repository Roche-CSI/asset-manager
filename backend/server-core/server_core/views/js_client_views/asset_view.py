import json
import logging

from asset_utils.common import exceptions
from flask import Blueprint, Response, request, make_response, current_app

from server_core.elastic.asset_entry import AssetEntry
from server_core.elastic.vector_search import ElasticVectorSearch
from server_core.models.asset import Asset
from server_core.models.asset_class import AssetClass
from server_core.models.asset_version import AssetVersion
from server_core.utils.json_encoder import to_json
from server_core.views.utils.asset_updater import update_asset_record
from server_core.views.utils.view_utils import compress_data, data_from_request

logger = logging.getLogger(__file__)

asset_view = Blueprint(name='dashboard_asset_view', import_name=__name__)

MAX_ALLOWED_TAGS = 10
MAX_TAG_LENGTH = 20


@asset_view.route('', methods=['GET'])
def list_assets():
    result = get_assets(args=request.args)
    compressed = compress_data(result)
    response = make_response(compressed)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-length'] = len(compressed)
    response.headers['Content-Encoding'] = 'gzip'
    return response


@asset_view.route('/<id>', methods=['GET'])
def get_asset(id: str):
    asset = Asset.get_if_exists(Asset.id == id)
    return Response(to_json(asset_data(asset)), mimetype="application/json", status=200)


def asset_data(asset: Asset):
    data = None
    if asset:
        versions = [version.to_dict() for version in asset.get_versions()]
        # object_ids = asset.version_counter.get().leaf_objects
        data = asset.to_dict()
        data['versions'] = versions
        data['all_objects'] = [obj.to_dict() for obj in asset.all_objects()]  # send as a dict
        data["root_version_id"] = asset.root_version().id
        data["leaf_version_id"] = asset.leaf_version().id
    return data


def get_assets(args: dict):
    if not args:
        return [node.to_dict(recurse=True) for node in Asset.public()]

    # client will ask if refs are valid before committing
    # we check and return the assets here
    if args.get("asset_names"):
        results = []
        asset_names = args.getlist("asset_names")
        for asset_name in asset_names:
            # refs are asset names
            class_name, seq_id = asset_name.split("/")
            class_id = args.get("class_id") or AssetClass.get_if_exists(AssetClass.name == class_name,
                                                                        AssetClass.project == args.get("project_id"))
            if class_id:
                asset = Asset.get_if_exists(Asset.asset_class == class_id, Asset.seq_id == seq_id)
                if asset:
                    # results.append({"id": asset.id, "name": asset.name})
                    results.append(asset_data(asset))
        return results

    if args.get("class_id"):
        # return [asset_data(asset) for asset in Asset.select().where(Asset.asset_class == args.get("class_id"))]
        page_number = int(args.get("page_number", 1))
        page_size = int(args.get("page_size", 15))
        search_by = args.get("search_by")
        seq_id = args.get("seq_id")
        alias = args.get("alias")
        owner = args.get("owner")
        data, page_count = Asset.list_assets(class_id=args.get("class_id"),
                                             seq_id=seq_id, alias=alias, owner=owner,
                                             page_number=page_number,
                                             page_size=page_size, search_by=search_by, recurse=True)
        json_data = []
        for asset in data:
            data = asset.to_dict()
            data["leaf_version"] = asset.leaf_version().to_dict(exclude=[AssetVersion.patch])
            json_data.append(data)
        return {"data": json_data, "page_count": page_count}

    elif args.get("alias"):
        # check if an alias exists
        asset = None
        class_id = args.get("class_id")
        if class_id:
            asset = Asset.get(Asset.asset_class == class_id, Asset.alias == args.get("alias"))
        return str({"id": asset.id, "name": asset.name})

    else:
        return None


@asset_view.route('/<id>', methods=['PUT'])
def update_asset(id: str):
    asset = Asset.get_if_exists(Asset.id == id)
    if not asset:
        return Response(to_json({"error": f"asset with id:{id} not found"}), mimetype="application/json", status=404)

    result = asset.to_dict()
    if request.method == "PUT":
        data = json.loads(request.data.decode("ascii"))
        try:
            result = update_asset_record(asset=asset, data=data)
        except Exception as e:
            logger.exception("Error occurred while updating the asset.")
            # append the error message to the status so response.raise_for_status() can get it
            if isinstance(e, exceptions.AssetException):
                return Response(to_json({"error": e.msg}), mimetype="application/json", status=f"500 {e.msg}")
            return Response(to_json({"error": str(e)}), mimetype="application/json", status=f"500 {e}")

    return Response(to_json(result), mimetype="application/json", status=200)


@asset_view.route('/add_to_index', methods=['POST'])
def add_to_index():
    """
    Endpoint to add documents to search engine's current index.
    Expects a list of JSON with the necessary asset fields.
    """
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    search: ElasticVectorSearch = current_app.search_engine
    try:
        asset_data = data_from_request(request)
        if not asset_data:
            return Response(
                to_json({"error": "Invalid or missing JSON payload"}),
                mimetype="application/json",
                status=400
            )

        # limit length
        max_docs = 10000
        if len(asset_data) > max_docs:
            return make_response(json.dumps({"error": f"Too many documents. Maximum allowed is {max_docs}"}), 400)

        # Add to index
        search_engine: ElasticVectorSearch = current_app.search_engine
        for data in asset_data:
            # Validate
            required_fields = ["id", "title", "description", "tags", "alias", "metadata"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return Response(
                    to_json({"error": f"Missing required fields: {', '.join(missing_fields)}"}),
                    mimetype="application/json",
                    status=400
                )
            else:
                asset = Asset.get_if_exists(Asset.id == data["id"])
                asset_class = asset.asset_class
                project = asset_class.project
                entry = AssetEntry.create(asset=asset,
                                          class_name=asset_class.name,
                                          class_id=str(asset_class.id),
                                          class_title=asset_class.title,
                                          class_status=asset_class.status,
                                          class_type=asset_class.class_type,
                                          project_name=project.name,
                                          project_title=project.title,
                                          project_id=str(project.id),
                                          project_status=project.status,
                                          es_score=None,
                                          es_highlight=None,
                                          )
                updated = entry.upsert(es=search, user=user)

        response = {
            "message": f"Added {len(asset_data)} documents to index."
        }
        return response, 201

    except Exception as e:
        logger.exception("Error occurred while adding a new asset entry.")
        return Response(
            to_json({"error": f"An error occurred: {str(e)}"}),
            mimetype="application/json",
            status=500
        )
