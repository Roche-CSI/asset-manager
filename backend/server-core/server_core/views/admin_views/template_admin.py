from server_core import models
from .read_write_admin import ReadWriteAdminView
from flask import flash
from flask_admin.babel import gettext


class TemplateAdmin(ReadWriteAdminView):
    can_delete = True
    column_list = ('name',
                   'description',
                   'readme',
                   'is_active',
                   'version',
                   'title',
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['name', 'version', 'created_by']
    form_columns = ['created_by', 'name', 'description', 'title', 'readme', 'version']

    def __init__(self):
        super().__init__(model=models.Template)

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
