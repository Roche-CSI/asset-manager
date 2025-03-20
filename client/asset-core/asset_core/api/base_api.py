import abc
import contextlib

from asset_core.store import AssetStore
from asset_utils.utils.log_utils import LoggingMixin


class BaseAPI(LoggingMixin):

    def __init__(self, store=None):
        # create a new store if not exists
        self.store = store or AssetStore.shared(create_if_not_exists=True)

    @contextlib.contextmanager
    def environment(self):
        try:
            self.set_environment()
            yield
        except Exception:
            raise
        finally:
            # need to unset the environment even if an exception is raised
            self.unset_environment()

    @abc.abstractmethod
    def set_environment(self):
        raise NotImplementedError

    @abc.abstractmethod
    def unset_environment(self):
        raise NotImplementedError
