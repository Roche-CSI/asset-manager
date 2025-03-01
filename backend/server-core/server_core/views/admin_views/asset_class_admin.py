from flask import flash
from server_core import models
from .readonly_admin import ReadOnlyAdminView


class AssetClassAdmin(ReadOnlyAdminView):
    column_list = ('id',
                   'project',
                   'name',
                   'title',
                   'description',
                   'class_type',
                   'created_at',
                   'created_by',
                   'modified_at',
                   'modified_by',
                   'attributes'
                   )
    column_searchable_list = ['title', 'name', 'class_type']

    def __init__(self):
        super().__init__(model=models.AssetClass)

    def write_yamls_to_bucket(self, ids):
        try:
            query = self.model.select().where(self.model.id << ids)
            updated = []
            for asset_class in query:
                class_url, class_list_url = asset_class.write_to_bucket()
                updated.append(str(asset_class.id))
            updated = ', '.join(updated)
            flash(f"Success!, {updated} asset-classes successfully updated.")
        except Exception as ex:
            flash(f"Failed to update Bucket. {str(ex)}s", 'error')
