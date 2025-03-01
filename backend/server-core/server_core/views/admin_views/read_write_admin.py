from flask_admin.contrib.peewee.form import get_form, \
    CustomModelConverter, InlineModelConverter, save_inline
from flask_admin.babel import gettext
from flask import flash
from .readonly_admin import ReadOnlyAdminView


class ReadWriteAdminView(ReadOnlyAdminView):
    can_edit = True
    can_create = True
    column_display_actions = True

    def create_model(self, form):
        try:
            model = self.model()
            form.populate_obj(model)
            self._on_model_change(form, model, True)
            model.save(user=form.created_by.data, force_insert=True)

            # For peewee have to save inline forms after model was saved
            save_inline(form, model)
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to create record. %(error)s', error=str(ex)), 'error')
                self.log.exception('Failed to create record.')

            return False
        else:
            self.after_model_change(form, model, True)

        return model

    def update_model(self, form, model):
        try:
            form.populate_obj(model)
            self._on_model_change(form, model, False)
            model.save(user=form.modified_by.data)

            # For peewee have to save inline forms after model was saved
            save_inline(form, model)
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to update record. %(error)s', error=str(ex)), 'error')
                self.log.exception('Failed to update record.')

            return False
        else:
            self.after_model_change(form, model, False)

        return True

