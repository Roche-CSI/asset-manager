from flask import current_app
from peewee import *
from server_core.models.asset import Asset
from server_core.elastic.asset_entry import AssetEntry
from server_core.configs import Configs
from server_core.app import create_app
from server_core.elastic.vector_search import  ElasticVectorSearch


def update_elatic():
    try:
        app = create_app()
        Configs.shared(mode=Configs.modes.DEV)
        app.db.connect()

        # Fetch all records from the Asset table
        assets = Asset.select().where(
            (Asset.alias.is_null(False)) |
            (Asset.tags.is_null(False)) |
            (Asset.metadata.is_null(False)) |
            (Asset.description.is_null(False)) |
            (Asset.title.is_null(False))
        )
        print(f"Found {len(assets)} assets")
        search: ElasticVectorSearch = current_app.search_engine
        for asset in assets:
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
            updated = entry.upsert(es=search, user='user1')

    except Exception as e:
        print(f"Error occurred while exporting data: {e}")
        app.db.close()

if __name__ == '__main__':
    update_elatic()  
