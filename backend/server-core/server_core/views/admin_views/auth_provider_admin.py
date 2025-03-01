from server_core import models
from .read_write_admin import ReadWriteAdminView


class AuthProviderAdmin(ReadWriteAdminView):
    column_list = ('id',
                   'name',
                   'description',
                   'configs',
                   'is_active',
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['name']
    form_columns = ['name',
                    'description',
                    'created_by',
                    'is_active',
                    'configs',
                    'modified_by']

    def __init__(self):
        super().__init__(model=models.AuthProvider)
