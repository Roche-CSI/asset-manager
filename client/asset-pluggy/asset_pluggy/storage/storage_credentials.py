from asset_utils.common.singleton import Singleton


class StorageCredentials(Singleton):

    def post_init(self):
        # default credentials for fetching asset and its contents i.e. files
        self._content_credentials: dict = {}
        # credentials for fetching only asset
        self._project_credentials: dict = {}
        self.use_content_credentials = False

    def set_content_credentials(self, cred: dict):
        """"always use for asset fetching only for most cases _content_credentials are same as _project_credentials"""
        self._content_credentials = cred

    def set_credentials(self, cred: dict):
        """always use for contents fetching only
         - credentials and asset_credentials could be same
         - only proxy assets, this would be different
        """
        self._project_credentials = cred

    @property
    def credentials(self) -> dict:
        """Return credentials based on the use_content_credentials flag"""
        if self.use_content_credentials:
            return self._content_credentials
        return self._project_credentials
