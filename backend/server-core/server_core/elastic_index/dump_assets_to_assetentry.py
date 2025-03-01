import os
import time
from peewee import *
from server_core.models.asset import Asset
from server_core.configs import Configs
from server_core.elastic.asset_entry import AssetEntry
from server_core.app import create_app
import json
from server_core.utils.file_utils import FileUtils
from server_core.elastic.vector_search import ElasticVectorSearch
from datetime import datetime

def datetime_converter(obj):
    """
    Custom function to convert datetime objects to strings.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO format
    raise TypeError("Type not serializable")


def export_to_json():
    try:
        Configs.shared(mode=Configs.modes.USER_TEST)
        app = create_app()
        app.db.connect()
        # Fetch all records from the Asset table
        assets = Asset.select().where(
            (Asset.alias.is_null(False)) |
            (Asset.tags.is_null(False)  & (fn.json_array_length(Asset.tags) > 0)) |
            (Asset.metadata.is_null(False) & (fn.json_array_length(fn.json_extract_path(Asset.metadata, '{}')) > 0)) |
            (Asset.description.is_null(False)) |
            (Asset.title.is_null(False))
        )
        print(f"Found {len(assets)} assets")
        assets_data = []
        for asset in assets:
            # Get the related AssetClass data
            asset_class = asset.asset_class
            project = asset_class.project 
            # Create a dictionary for the asset entry
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
          
            assets_data.append(entry.to_dict())

        # Write the list to a JSON file, using the custom datetime converter
        with open('t_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(assets_data, json_file, indent=4, default=datetime_converter)

    except Exception as e:
        print(f"Error occurred while exporting data: {e}")
        app.db.close()


def run_test():
    """Run a test with various metadata values and timing measurements"""
    from server_core.elastic.asset_entry import AssetEntry

    search_engine = ElasticVectorSearch.shared(host=os.getenv("ELASTIC_HOST", "localhost:9200"))

    # Create index
    print("\nCreating index...")
    start = time.time()
    AssetEntry.create_index(es=search_engine, exists_ok=True)
    print(f"Index creation took: {time.time() - start:.2f} seconds")

    start_total = time.time()
    # Load test data
    start = time.time()
    test_documents = FileUtils.read_json(os.path.join(os.path.dirname(__file__), "assets_filtered_data.json"))
    print(f"\nLoading test data took: {time.time() - start:.2f} seconds")

    try:
        # Index documents
        print("\nIndexing test documents...")
        start = time.time()
        for doc in test_documents:
            doc_id = doc['id']
            exists = search_engine.document_exists(index_name=AssetEntry.index_name(), doc_id=doc_id)
            if exists:
                search_engine.update_document(index_name=AssetEntry.index_name(), document=doc)
                print("Document Updated, doc Id: ", doc_id, " entry updated")
                continue
            else:
                AssetEntry.index_document(es=search_engine, data=doc)

        indexing_time = time.time() - start
        print(f"Indexing {len(test_documents)} documents took: {indexing_time:.2f} seconds")
    
    except Exception as e:
        raise e


if __name__ == '__main__':
    export_to_json()  
    run_test()
