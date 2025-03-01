from peewee import *
from playhouse.postgres_ext import JSONField
from server_core.models.webhook import Webhook
from server_core.models.base.read_only import ReadOnlyModel


class WebhookStatus(ReadOnlyModel):
    webhook = ForeignKeyField(Webhook, backref='statuses', on_delete='CASCADE', null=False)
    status = CharField(null=True)  # success, failure, timeout etc
    payload = JSONField(null=True)  # request payload
    response = TextField(null=True)  # error message, etc.

