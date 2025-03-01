import logging


class LoggingMixin:

    @classmethod
    def logger(cls) -> logging.Logger:
        return logging.getLogger(cls.__module__ + "." + cls.__name__)

    @property
    def log(self) -> logging.Logger:
        try:
            return self._log
        except AttributeError:
            self._log = self.__class__.logger()
            return self._log
