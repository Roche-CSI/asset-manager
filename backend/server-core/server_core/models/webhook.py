from peewee import *
from server_core.asset_client.exceptions import AssetException
from server_core.models.base.read_write import ReadWriteModel
from playhouse.postgres_ext import JSONField
from server_core.models.utils.webhook import trigger_webhook

EVENT_TYPES = ["update", "create", "delete", "deprecate", "obsolote"]
ENTITY_TYPES = ["asset_class", "asset", "project"]

ENTITY_CHOICES = (("project", 'Project'), ("asset_class", 'AssetClass'), ("asset", 'Asset'))


class Webhook(ReadWriteModel):
    entity_type = CharField(null=False, choices=ENTITY_CHOICES)  # asset_class, asset, project etc.
    entity_id = CharField(null=False)
    name = CharField(null=False)  # no spaces in name
    title = CharField(null=True)
    description = TextField(null=True)
    webhook_url = CharField(null=False)
    event_type = CharField(null=False, default="n/a")  # update, create, delete, deprecate, obsolote etc.
    event_source = CharField(null=False, choices=ENTITY_CHOICES)  # source of event, e.g. asset, asset_class, project etc.
    attributes = JSONField(null=False)  # scheduled, active, deprecated, obsolete etc.

    class Meta:
        indexes = (
            (('entity_type', 'entity_id'), False),  # index on entity and entity_id for faster queries
        )

    def save(self, user=None, force_insert=False, only=None):
        # check if name contains spaces
        if " " in self.name:
            raise AssetException("Event name cannot contain spaces")
        self.name = self.name.lower()
        if self.event_type not in EVENT_TYPES:
            raise AssetException(f"Event type must be one of {EVENT_TYPES}")
        return super().save(user=user, force_insert=force_insert, only=only)

    def dispatch(self, data):
        payload = {"event": {"name": self.name, "event_type": self.event_type, "data": data}}
        trigger_webhook(url=self.webhook_url, payload=payload)

    def status_callback(self, success: bool, payload, response_or_exception):
        from server_core.models.webhook_status import WebhookStatus
        if success:
            status = "success"
            details = f"Status code: {response_or_exception.status_code}"
        else:
            status = "failed"
            details = f"Error: {str(response_or_exception)}"

        WebhookStatus.create(
            webhook=self,
            status=status,
            payload=payload,
            response=details,
            user="system"
        )
