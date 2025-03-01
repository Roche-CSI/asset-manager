import json
from .read_write_admin import ReadWriteAdminView
from server_core import models


class AssetAdmin(ReadWriteAdminView):
    can_delete = False
    can_create = False
    can_edit = True

    column_list = ('id',
                   'asset_class',
                   'seq_id',
                   "title",
                   'description',
                   "attributes",
                   "metadata",
                   "tags",
                   'frozen',
                   'created_at',
                   'created_by',
                   )

    column_searchable_list = ['title', "description"]
    column_sortable_list = ['id', 'title']
    column_default_sort = ("created_at", True)
    form_columns = ["title",
                    'description',
                    "attributes",
                    "metadata",
                    'modified_by']

    def __init__(self):
        super().__init__(model=models.Asset)

    def after_model_change(self, form, model, is_created):
        # todo: write to bucket
        print("after_model_update")
        print(json.dumps(model.to_dict()))
        pass
