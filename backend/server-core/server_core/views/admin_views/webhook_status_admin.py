from server_core import models
from .readonly_admin import ReadOnlyAdminView
from flask import flash
from flask_admin.babel import gettext


class WebhookStatusAdmin(ReadOnlyAdminView):
    can_delete = True
    column_list = ('webhook',
                   'status',
                   'payload',
                   'response',
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['created_by']

    def __init__(self):
        super().__init__(model=models.WebhookStatus)

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

