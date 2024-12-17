from asset_pluggy.storage import BlobStoreURL


class MountedBlobStoreURL(BlobStoreURL):
    def __init__(self, url: str, **kwargs):
        """The url here could either be a posix path or a URL

        We do the necessary conversion here
        """
        self.mount_cfg = kwargs.pop("mount_cfg")
        super().__init__(url, **kwargs)

        if self.is_remote():
            self.posix_url = self.mount_cfg.url_to_posix(url)
        elif self.mount_cfg.is_posix(url):
            self.posix_url = url
            self.url = self.mount_cfg.posix_to_url(url)
        else:
            # url is a posix path outside the mount directory
            # i.e. when uploading an asset or downloading metadata to temp directory
            # just set posix_url, no conversion needed
            self.posix_url = url

    def __str__(self):
        return f"MountedBlobStoreURL(url={self.url}, path={self.posix_url})"
