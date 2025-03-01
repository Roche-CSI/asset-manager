from .readonly_admin import ReadOnlyAdminView
from server_core import models


class ContentAdmin(ReadOnlyAdminView):
    column_list = ('id',
                   'mime_type',
                   'hash',
                   'size',
                   'meta',
                   'created_at',
                   'created_by',
                   )

    def __init__(self):
        super().__init__(model=models.Content)