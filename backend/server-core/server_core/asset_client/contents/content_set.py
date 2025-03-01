from server_core.utils.better_set import BetterSet
from .content_factory import ContentFactory
from .content import Content
from collections.abc import Callable
import os


class ContentSet(BetterSet):
    asset = None

    def __init__(self, *args, asset=None):
        super().__init__(*args)
        self.asset = asset

    @property
    def staging_url(self):
        return os.path.join(self.asset.configs.contents_url(staging=True), self.asset.asset_class.id)

    @property
    def remote_url(self):
        return os.path.join(self.asset.configs.contents_url(staging=False), self.asset.asset_class.id)

    def filter(self, predicate: Callable = None) -> [Content]:
        """returns a dict of assets stored in asset-manifest
        Parameters:
            predicate: lambda function
        """
        if not predicate:
            return list(self)
        return [content for content in self if predicate(content)]

    def add_or_update(self, content: Content):
        existing: Content = self.get(content)
        if existing:
            existing.state = Content.states.STAGED
            return existing

        content.state = Content.states.STAGED
        self.add(content)
        return content

    def de_serialize(self, **kwargs):
        content = ContentFactory().de_serialize(**kwargs)
        if content in self:
            content = self.get(content)  # get the stored content
        else:
            self.add(content)
        return content


