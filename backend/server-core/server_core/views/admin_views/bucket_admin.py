from server_core import models
from .read_write_admin import ReadWriteAdminView
from flask import flash
from flask_admin.babel import gettext


class BucketAdmin(ReadWriteAdminView):
    can_delete = True
    column_list = ('title',
                   'bucket_url',
                   'keys',
                   'description',
                   'is_active',
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['bucket_url', 'created_by']
    form_columns = ['created_by', 'title', 'bucket_url', 'keys', 'description', 'modified_by']

    def __init__(self):
        super().__init__(model=models.Bucket)

    def delete_model(self, model):
        try:
            username = 'system'
            self.on_model_delete(model)
            model.delete_instance(user=username, recursive=True, permanently=True)
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                self.log.exception('Failed to delete record.')
            return False
        else:
            self.after_model_delete(model)

        return True
