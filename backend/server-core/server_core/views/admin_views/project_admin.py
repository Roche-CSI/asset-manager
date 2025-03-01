from server_core import models
from .read_write_admin import ReadWriteAdminView
from flask import flash
from flask_admin.babel import gettext


class ProjectAdmin(ReadWriteAdminView):
    can_delete = True
    column_list = ('id',
                   'name',
                   "title",
                   'description',
                   'is_active',
                   "staging_url",
                   "remote_url",
                   "credentials_user",
                   "credentials_server",
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['name']
    form_columns = ['name',
                    "title",
                    'description',
                    'is_active',
                    'staging_url',
                    'remote_url',
                    'credentials_user',
                    'credentials_server',
                    'created_by',
                    'modified_by']

    def __init__(self):
        super().__init__(model=models.Project)

    def delete_model(self, model):
        try:
            username = self.get_username()
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