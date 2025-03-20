import os
from typing import Iterable, Callable

from asset_utils import common
from asset_utils.utils import utils
from .content import Content


class ContentSet(common.BetterSet):
    asset = None

    def __init__(self, *args, asset=None):
        super().__init__(*args)
        self.asset = asset

    @property
    def staging_url(self):
        return os.path.join(self.asset.repo.contents_url(staging=True), self.asset.top_hash)

    @property
    def remote_url(self):
        url = os.path.join(self.asset.repo.contents_url(staging=False), self.asset.top_hash)
        return url

    @property
    def cache_dir(self):
        return self.asset.contents_cache_dir

    @property
    def size(self):
        data_size = 0
        for item in self:
            data_size += item.size
        return data_size

    def filter(self, predicate: Callable = None) -> [Content]:
        """Returns a dict of assets stored in asset-manifest

        Parameters:
            predicate: lambda function
        """
        if not predicate:
            return list(self)
        return [content for content in self if predicate(content)]

    def add_content(self, content: Content) -> Content:
        """Adds or updates the set with new content

        If the content exists, then we return the already stored content
        this is because we need to increase the ref count for that content
        """
        if content in self:
            existing: Content = self.get(content)
            # combine the linked objects
            existing.linked_objects = existing.linked_objects.union(content.linked_objects)
            return self.get(content)

        self.add(content)
        return content

    def save(self):
        self.update_states()
        self.update_file_stats()
        self.asset.states_db.update(**{"content_states": self.get_states()})
        self.asset.content_stats_db.update(**{"stats": self.get_file_stats()})

    def de_serialize(self, **kwargs):
        from asset_contents.content_factory import ContentFactory
        content = ContentFactory().de_serialize(**kwargs)
        if content in self:
            content = self.get(content)  # get the stored content
        else:
            self.add(content)
        return content

    def get_states(self):
        try:
            return self._states
        except AttributeError:
            self._states = self.asset.states_db.get_content_states()
            return self._states

    def set_states(self, x, save=False):
        self._states = x
        if save:
            self.asset.states_db.update(**{"content_states": self._states})

    def update_states(self, contents: Iterable[Content] = None, save=False):
        contents = contents or self
        updates = {content.id: content.get_state() for content in contents}
        self.set_states(utils.update_dict(self.get_states(), updates), save)

    def get_file_stats(self):
        try:
            return self._file_stats
        except AttributeError:
            self._file_stats = self.asset.content_stats_db.get_stats()
            return self._file_stats

    def set_file_stats(self, x: dict, save=False):
        self._file_stats = x
        if save:
            self.asset.content_stats_db.update(**{"stats": self._file_stats})

    def update_file_stats(self, contents: Iterable[Content] = None, save=False):
        contents = contents or self
        updates = {content.file_id: content.get_content_stat() for content in contents}
        for key, val in updates.items():
            if val:
                updates[key] = val.serialize()
        file_stats = {
            **self.get_file_stats(),
            **updates
        }
        self.set_file_stats(file_stats, save=save)

    def exists(self):
        for content in self:
            if not content.exists():
                return False
        return True
