from .content import Content, StorageSystems


class UrlContent(Content):

    @classmethod
    def storage_system_id(cls):
        return StorageSystems.URL

    def compute_stat(self):
        pass

    @property
    def remote_url(self):
        pass

    @property
    def staging_url(self):
        pass

    @property
    def cache_path(self):
        pass

    def add_ref(self, **kwargs):
        pass

    def remove_ref(self, **kwargs):
        pass

    def clear_from_cache(self):
        pass

    @property
    def can_stage(self) -> bool:
        pass

    async def upload_to_staging(self, **kwargs):
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
