from server_core import models
from .read_write_admin import ReadWriteAdminView
from flask import flash
from flask_admin.babel import gettext


class WebhookAdmin(ReadWriteAdminView):
    can_delete = True
    column_list = ('entity_type',
                   'entity_id',
                   'name',
                   'title',
                   'description',
                   'webhook_url',
                   'event_type',
                   'event_source',
                   'attributes',
                   'created_at',
                   'created_by',
                   )
    column_searchable_list = ['name', 'title', 'entity_type', 'entity_id', 'created_by']
    form_columns = ['entity_type', 'entity_id', 'name', 'title', 'description', 'webhook_url', 'event_type', 'event_source', 'attributes', 'created_by']

    def __init__(self):
        super().__init__(model=models.Webhook)

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

