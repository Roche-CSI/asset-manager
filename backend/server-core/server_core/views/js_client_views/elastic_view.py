import json
import logging
from urllib.parse import unquote

from flask import Blueprint, Response, request, current_app

from server_core.elastic.asset_entry import AssetEntry
from server_core.elastic.vector_search import ElasticVectorSearch
from server_core.utils import json_encoder

logger = logging.getLogger(__file__)

view = Blueprint(name='elastic_search_view', import_name=__name__)


@view.route('', methods=['GET'])
def search():
    """Perform a global search in Elasticsearch based on query params"""
    # Extract query parameters
    user = request.args.get('user')
    if not user:
        return Response(
            json_encoder.to_json({"error": "missing required param: user"}),
            mimetype="application/json",
            status=400
        )

    query = unquote(request.args.get('query'))
    if not query:
        return Response(
            json_encoder.to_json({"error": "missing required param: query"}),
            mimetype="application/json",
            status=400
        )

    filters = json.loads(request.args.get('filters', '{}'))
    # remove empty filters
    filters = {k: v for k, v in filters.items() if v}
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    try:
        search: ElasticVectorSearch = current_app.search_engine
        records, count = AssetEntry.search(es=search,
                                           query=query,
                                           filters=filters,
                                           size=page_size,
                                           offset=(page - 1) * page_size)

        result = {
            "total": len(records),
            "page": page,
            "page_size": page_size,
            "results": [entry.to_dict(fields=entry.frontend_fields()) for entry in records if entry]
        }
        return Response(json_encoder.to_json(result), mimetype="application/json", status=200)

    except Exception as e:
        logger.exception("Error during Elasticsearch search")
        return Response(
            json_encoder.to_json({"error": str(e)}),
            mimetype="application/json",
            status=500
        )


@view.route('', methods=['POST'])
def create():
    """Create or update a document in Elasticsearch"""
    user = request.args.get('user')
    if not user:
        return Response(
            json_encoder.to_json({"error": "missing required param: user"}),
            mimetype="application/json",
            status=400
        )

    try:
        data = request.get_json()
        if not data or type(data) is not dict:
            return Response(
                json_encoder.to_json({"error": "missing request body"}),
                mimetype="application/json",
                status=400
            )

        search: ElasticVectorSearch = current_app.search_engine
        response = AssetEntry.upsert_document(es=search, data=data, user=user)
        # Check the operation result
        operation = response['result']  # Will be either 'created' or 'updated'
        status = 201 if operation == 'created' else 200

        return Response(
            json_encoder.to_json({
                "message": f"Document successfully {operation}",
                "result": response['result'],
                "version": response['_version']
            }),
            mimetype="application/json",
            status=status
        )

    except Exception as e:
        logger.exception("Error creating/updating document")
        return Response(
            json_encoder.to_json({"error": str(e)}),
            mimetype="application/json",
            status=500
        )
