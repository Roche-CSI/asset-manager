from __future__ import annotations

import os.path
from typing import Callable

from asset_utils.common import exceptions
from asset_utils.utils.file_utils import FileUtils


class TransportResource:

    def __init__(self,
                 src: str,
                 dst: str,
                 hash: tuple = None,
                 callback: Callable = None,
                 **kwargs):
        self.src = src
        self.dst = dst
        self.src_hash = hash  # (hash_type, hash_value)
        self.callback = callback

    def __eq__(self, other: TransportResource):
        return self.src == other.src

    def __hash__(self):
        return hash(self.src)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.src)

    @property
    def dst_hash(self):
        try:
            return self._dst_hash
        except AttributeError:
            self._dst_hash = self.compute_dest_hash(hash_type=self.src_hash[0])
            return self._dst_hash

    @dst_hash.setter
    def dst_hash(self, x: tuple):
        self._dst_hash = x

    def validate(self) -> None:
        """The base implementation assumes files are available locally.
        Subclasses must override and provide their own implementation
        """
        if not os.path.exists(self.src):
            raise exceptions.InvalidObjectSourceError(f"file not found: {self.src}")

    def on_transfer_complete(self, *args):
        if self.callback:
            self.callback(*args)

    def verify_checksum(self):
        if not self.src_hash:
            return False
        ht, hv = self.dst_hash
        if ht != self.src_hash[0] or hv != self.src_hash[1]:
            return False
        return True

    def compute_dest_hash(self, hash_type: str):
        """subclass can override"""
        return FileUtils.file_hash(abs_path=self.dst, hash_type=hash_type)
