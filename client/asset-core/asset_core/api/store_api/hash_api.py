from asset_contents.content_factory import ContentFactory
from asset_utils.common import exceptions
from asset_utils.utils.log_utils import LogColors
from .store import StoreAPI


class ContentHashAPI(StoreAPI):

    def run(self, args):
        pass

    def content_hash(self, src):
        # using print here because userlog add extra chars for color formatting
        # hash of hashes in case the user passes a directory
        # should accept wildcard
        try:
            hash = ContentFactory().compute_hash(src)
            print(hash)
        except exceptions.InvalidObjectSourceError as e:
            self.user_log.message(e.msg, LogColors.ALERT)
