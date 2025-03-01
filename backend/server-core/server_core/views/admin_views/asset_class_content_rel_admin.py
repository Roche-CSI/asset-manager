from .readonly_admin import ReadOnlyAdminView
from server_core import models


class AssetClassContentRelationsAdmin(ReadOnlyAdminView):
    column_list = ('id',
                   'asset_class',
                   'content',
                   'created_at',
                   'created_by',
                   )

    def __init__(self):
        super().__init__(model=models.AssetClassContentRelations)