from server_core import models
from .read_write_admin import ReadWriteAdminView


class AssetSettingsAdmin(ReadWriteAdminView):
    column_list = ('id',
                   'name',
                   'description',
                   'value',
                   'modified_by',
                   'created_by',
                   )
    form_columns = ['name',
                    'description',
                    'value',
                    'modified_by',
                    'created_by',
                    ]

    def __init__(self):
        super().__init__(model=models.AssetSettings)
