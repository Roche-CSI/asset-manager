from .content import Content, StorageSystems


class UrlContent(Content):

    @classmethod
    def storage_system_id(cls):
        return StorageSystems.URL

    def compute_file_stat(self):
        pass

    @property
    def remote_url(self):
        pass

    @property
    def staging_url(self):
        pass

    async def transfer_to_remote(self, **kwargs):
        pass

    def serialize(self) -> dict:
        pass

    @classmethod
    def serialize_fields(cls):
        pass

    @classmethod
    def de_serialize(cls, asset, data: dict) -> Content:
        pass

    @classmethod
    def create(cls, **kwargs) -> Content:
        pass

    @classmethod
    def compute_hash(cls, **kwargs):
        pass

    def is_deleted(self) -> bool:
        pass

    def is_modified(self) -> bool:
        pass

    def is_renamed(self) -> bool:
        pass