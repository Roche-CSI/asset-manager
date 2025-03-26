import json
import logging

from flask import Blueprint, Response, request

from server_core.models.asset import Asset
from server_core.models.asset_class import AssetClass
from server_core.models.asset_version import AssetVersion
from server_core.models.tag_queries import TagQueries
from server_core.models.tag_refs import TagRefs
from server_core.models.tags import Tags
from server_core.utils import json_encoder
from server_core.utils.json_encoder import to_json
from server_core.views.utils import view_utils

logger = logging.getLogger(__file__)

tags_view = Blueprint(name='db_tags_view', import_name=__name__)


@tags_view.route('', methods=['GET', 'POST', 'PUT'])
def index():
    if request.method == 'GET':
        return get_tags()
    elif request.method == "POST":
        return create_tags()
    elif request.method == "PUT":
        return update_tags()


def create_tags():
    """ Create tags record using the tag dictionary, table_name, record_id from user input

    data
    ----------
    user: user id
    tags: a list of dictionaries {tag_name: tag_name, tag_value: tag_value, is_primary: True/False}
    table_name: table name (asset_class/asset/asset_version) of the record to which the tag dictionary is attached
    record_id: record id in its corresponding table
    """
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    table_name = data.get("table_name")
    record_id = data.get("record_id")
    tags: list = data.get("tags")
    validated = Tags.validate_tags(tags)
    result = create_tags_helper(tags=tags,
                                user=user,
                                table_name=table_name,
                                record_id=record_id)
    res_code = 201  # created
    return Response(to_json(result), mimetype="application/json", status=res_code)


def create_tags_helper(tags: list, user: str, table_name: str, record_id: str):
    tag_ids = []
    all_tags = {}
    result = []
    for tag in tags:
        tag_name = tag.get("tag_name")
        tag_value = tag.get("tag_value")
        is_primary = tag.get("is_primary")
        tag_record: Tags = Tags.create_if_not_exists(user=user,
                                                     tag_name=tag_name,
                                                     tag_value=tag_value)
        tag_ids.append(tag_record.id)
        tag_ref: TagRefs = TagRefs.create_if_not_exists(user=user,
                                                        tag_id=tag_record.id,
                                                        table_name=table_name,
                                                        record_id=record_id,
                                                        is_primary=is_primary
                                                        )
        result.append(tag_ref)
        all_tags[tag_name] = tag_value
    tag_hash = TagQueries.compute_tag_hash(tag_ids=tag_ids)
    tag_query = TagQueries.create_if_not_exists(user=user,
                                                tag_hash=tag_hash,
                                                table_name=table_name,
                                                record_id=record_id,
                                                result=all_tags
                                                )
    return result


def get_tags():
    """
    Returns a list of tag_refs for a table record, based on query params
    This method implements inheritance based on tag_queries's query priority dict
    """
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    table_name = request.args.get('table_name')
    record_id = request.args.get('record_id')
    query_priority = TagQueries.QUERY_PRIORITY
    for query_table in query_priority:
        if table_name == query_table:
            query = TagRefs.list_tag_refs(table_name=table_name, record_id=record_id)
            result = [record.to_dict(recurse=True) for record in query]
            if result:
                return Response(json_encoder.to_json(result), mimetype="application/json", status=200)
            else:  # if not, look for its parent's tags ( parent is either asset or asset_class table)
                if table_name == "asset_version":
                    version_record: AssetVersion = AssetVersion.get(AssetVersion.id == record_id)
                    asset_id = version_record.asset_id
                    record_id = asset_id
                    table_name = "asset"
                elif table_name == "asset":
                    asset_record: Asset = Asset.get(Asset.id == record_id)
                    asset_class_id = asset_record.asset_class_id
                    record_id = asset_class_id
                    table_name = "asset_class"
    return Response(json_encoder.to_json([]), mimetype="application/json", status=200)


def update_tags():
    data: dict = view_utils.data_from_request(request)
    user = data.get("user")
    if not user:
        raise Exception("missing required param: user")
    table_name = data.get("table_name")
    record_id = data.get("record_id")
    tags: list = data.get("tags")
    validated = Tags.validate_tags(tags)

    existing_tag_refs = TagRefs.list_tag_refs(table_name=table_name, record_id=record_id)
    for tag_ref in existing_tag_refs:
        tag_ref.delete_instance(user=user, recursive=True, permanently=True)
    existing_tag_queries = TagQueries.select().where(
        (TagQueries.table_name == table_name) &
        (TagQueries.record_id == record_id)
    )
    for tag_query in existing_tag_queries:
        tag_query.delete_instance(user=user, recursive=True, permanently=True)
    result = create_tags_helper(tags=tags,
                                user=user,
                                table_name=table_name,
                                record_id=record_id)
    res_code = 200  # OK
    return Response(to_json(result), mimetype="application/json", status=res_code)


@tags_view.route('/searches', methods=['GET'])
def search_by_tags():
    """
    Return a list of asset classes or assets if their tags matches the search query
    """
    tags: list = json.loads(request.args.get('tags'))
    result = {"error": '', "records": []}
    # First, find id for each tag and compute tag hash
    tag_ids = []
    for tag in tags:
        tag_name = tag.get("tag_name")
        tag_value = tag.get("tag_value")
        tag_record: Tags = Tags.get_if_exists(Tags.tag_name == tag_name, Tags.tag_value == tag_value)
        if tag_record:
            tag_ids.append(tag_record.id)
        else:
            result["error"] += f'{{{tag_name}: {tag_value}}} is not a valid tag. '
    tag_hash = TagQueries.compute_tag_hash(tag_ids=tag_ids)
    project_id = request.args.get("project_id")
    asset_class_id = request.args.get("asset_class_id")
    record_table_name = "asset_class" if project_id else "asset"
    records = []
    if tag_ids:  # search using tag hash first then tag refs
        query = TagQueries.select().where(
            (TagQueries.tag_hash == tag_hash) &
            (TagQueries.table_name == record_table_name)
        )
        record_ids = [record.record_id for record in query]
        records = get_records_by_ids(record_ids, project_id, asset_class_id)
        if not records:  # if no exact match, partial search
            record_ids = set()
            for tag_id in tag_ids:
                query = TagRefs.select().where(
                    (TagRefs.tag_id == tag_id) &
                    (TagRefs.table_name == record_table_name)
                )
                record_ids.update([tag_ref.record_id for tag_ref in query])
            records = get_records_by_ids(record_ids, project_id, asset_class_id)
    result["records"] = records
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)


def get_records_by_ids(record_ids: [], project_id: str, asset_class_id: str):
    """
    Return a list of asset classes in project_id if project_id is given
    else a list of assets in asset_class_id
    """
    result = []
    for record_id in record_ids:
        if project_id:
            asset_class: AssetClass = AssetClass.get_if_exists(
                AssetClass.id == record_id,
                AssetClass.project_id == project_id
            )
            result.append(asset_class.to_dict()) if asset_class else None
        else:
            asset: Asset = Asset.get_if_exists(
                Asset.id == record_id,
                Asset.asset_class_id == asset_class_id
            )
            result.append(asset.to_dict()) if asset else None
    return result


@tags_view.route('/list_tags', methods=['GET'])
def list_tags():
    """Returns a list of all tags"""
    user = request.args.get('user')
    if not user:
        raise Exception("required param missing: user")
    result = [record.to_dict() for record in Tags.public()]
    return Response(json_encoder.to_json(result), mimetype="application/json", status=200)
