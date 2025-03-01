from server_core.utils.logging import LoggingMixin
from .configs import Configs


class StorageHandler(LoggingMixin):
    credentials = None
    staging_url = None
    remote_url = None

    def __init__(self, credentials: dict, staging_url: str, remote_url: str):
        self.credentials = credentials
        self.staging_url = staging_url
        self.remote_url = remote_url

    def __enter__(self):
        Configs.shared().storage_credentials = self.credentials
        Configs.shared().set_storage_urls(staging_url=self.staging_url,
                                          remote_url=self.remote_url)

    def __exit__(self, exc_type,exc_value, exc_traceback):
        Configs.shared().storage_credentials = None
        Configs.shared().clear_storage_urls()