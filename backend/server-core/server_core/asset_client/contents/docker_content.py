from .content import Content, StorageSystems


class DockerContent(Content):

    def __init__(self, **kwargs):
        super().__init__(**self.validate_kwargs(kwargs))

    @classmethod
    def storage_system_id(cls):
        return StorageSystems.GCR

    # @property
    # def can_stage(self):
    #     return False
