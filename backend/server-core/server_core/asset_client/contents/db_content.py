from .content import Content


class DbContent(Content):
    @property
    def remote_url(self):
        pass

    @property
    def staging_url(self):
        pass

    @property
    def cache_path(self):
        pass

    def link(self, **kwargs):
        pass

    def unlink(self, **kwargs):
        pass

    def clear_from_cache(self):
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
    def bulk_create(cls, **kwargs) -> [Content]:
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