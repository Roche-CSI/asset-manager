from asset_pluggy.storage import StorageData
from asset_plugin_gcr.gcr_url import GcrURL


class GcrBlob(StorageData):
    url = None
    host: str = None
    name: str = None
    tag: str = None
    content_type: str = None
    hashes: dict = {}

    def initialize(self, data: dict, url_object: GcrURL) -> None:
        """
        Parameters
        ----------
        data: dict
            The data to initialize the blob with
        url_object: GcrURL
            The URL object that the blob is associated with
        """
        self.name = data.get("name")
        self.tag = data.get("tag")
        self.content_type = data.get("mediaType")
        self.hashes[data.get("hash_type")] = data.get("hash_value")
        self.size = int(data.get("imageSizeBytes"))
        self.host = url_object.host
        self.url = url_object.url_for_blob(host=self.host, name=self.name,
                                           hash_type=data.get("hash_type"),
                                           hash_value=data.get("hash_value"))
