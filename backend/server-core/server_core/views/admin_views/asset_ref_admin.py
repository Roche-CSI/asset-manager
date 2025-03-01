from .readonly_admin import ReadOnlyAdminView
from server_core import models


class AssetRefAdmin(ReadOnlyAdminView):
    column_list = ('id',
                   'src_version',
                   'dst_version',
                   'label',
                   'properties',
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['label']

    def __init__(self):
        super(AssetRefAdmin, self).__init__(model=models.AssetRef)
