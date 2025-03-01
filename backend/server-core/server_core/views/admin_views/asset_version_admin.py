from server_core import models
from .readonly_admin import ReadOnlyAdminView


class AssetVersionAdmin(ReadOnlyAdminView):
    column_list = ('id',
                   'asset',
                   'parent',
                   'commit_hash',
                   'commit_message',
                   'created_at',
                   'created_by',
                   'size'
                   )

    def __init__(self):
        super().__init__(model=models.AssetVersion)
