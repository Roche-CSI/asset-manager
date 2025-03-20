import re

from asset_utils.common import exceptions


class MountConfig:
    def __init__(self, mount: str, url: str):
        self.mount = mount
        self.url = url

    def __str__(self):
        return f"MountConfig(mount={self.mount}, url={self.url})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.mount == other.mount and self.url == other.url

    def __hash__(self):
        return hash((self.mount, self.url))

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def sanitize_path(path: str) -> str:
        """Remove any extra slashes from the path while preserving protocol identifiers."""
        # Preserve the protocol identifier if present
        protocol_match = re.match(r'^(\w+:\/\/)', path)
        protocol = protocol_match.group(1) if protocol_match else ''

        # Remove the protocol for now
        path_without_protocol = re.sub(r'^\w+:\/\/', '', path)

        # Replace multiple slashes with a single slash
        sanitized_path = re.sub(r'\/+', '/', path_without_protocol)

        # Reattach the protocol
        return protocol + sanitized_path

    def url_to_posix(self, url: str) -> str:
        """Translates the given URL to the mounted path"""
        if not self.is_url(url):
            raise exceptions.AssetException(f"URL {url} does not start with {self.url}")
        return self.sanitize_path(url.replace(self.url, self.mount))

    def posix_to_url(self, posix: str) -> str:
        """Translates the given mounted path to the URL"""
        if not self.is_posix(posix):
            raise exceptions.AssetException(f"Posix path {posix} does not start with {self.mount}")
        return self.sanitize_path(posix.replace(self.mount, self.url))

    def is_posix(self, path: str) -> bool:
        """Checks if the given path is a mounted path"""
        return path.startswith(self.mount)

    def is_url(self, url: str) -> bool:
        """Checks if the given URL is a mounted URL"""
        return url.startswith(self.url)
