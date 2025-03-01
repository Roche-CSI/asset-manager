from asset_pluggy.storage.storage_factory import StorageFactory
from asset_pluggy.storage.transporter import Transporter
from asset_utils.utils.in_memory_file import InMemoryFile
from peewee import *
from playhouse.postgres_ext import JSONField

from server_core.configs import Configs
from .base.read_write import ReadWriteModel
from .project import Project


class AssetClass(ReadWriteModel):
    project = ForeignKeyField(Project, backref='asset_classes', on_delete='CASCADE', null=False)
    name = CharField(unique=False)
    counter = IntegerField(default=0)
    owner = CharField(null=False)
    title = CharField(null=False, default="n/a")
    description = TextField(null=False, default="n/a")
    readme = TextField(null=True)
    class_type = CharField(null=False, default="n/a")
    attributes = JSONField(default=dict)  # attributes of the asset class
    metadata = JSONField(null=True, default=dict)  # additional metadata

    class Meta:
        indexes = (
            (('project', 'name'), True),
        )

    @classmethod
    def create(cls, user=None, **query):
        query["owner"] = query.get("owner", user)
        return super(AssetClass, cls).create(user, **query)

    def increment_asset_seq(self, user=None):
        # increment counter
        self.counter += 1
        self.save(user=user, only=[self.__class__.counter])
        return self.counter

    @classmethod
    def yaml_fields(cls):
        return [
            "id",
            "name",
            "project",
            "created_at",
            "created_by",
            "owner",
            "title",
            "description",
            "class_type",
            "modified_at",
            "modified_by",
            "attributes",
            "status",
            "metadata"
        ]

    def write_to_bucket(self) -> str:
        with self.project.storage():
            class_data = {
                "file": InMemoryFile(file_ext=".yaml", file_data=self.to_dict()),
                "url": self.yaml_url
            }
            class_list = {record.name: str(record.id) for record in self.project.asset_classes}
            class_list_data = {
                "file": InMemoryFile(file_ext=".yaml", file_data=class_list),
                "url": Configs.shared().class_list_url
            }
            storage = StorageFactory.storage_for_url(src_url=self.yaml_url)
            transporter: Transporter = storage.get_transporter()
            transporter.write_to_bucket(data=[
                class_data,
                class_list_data
            ])
            return self.yaml_url, Configs.shared().class_list_url

    @property
    def yaml_url(self):
        return Configs.shared().asset_class_url(class_id=str(self.id))
