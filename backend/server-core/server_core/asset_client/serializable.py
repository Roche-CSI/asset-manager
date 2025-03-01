import abc


class Serializable(abc.ABC):
    """Serializable protocol"""

    @classmethod
    @abc.abstractmethod
    def de_serialize(cls, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def serialize(self) -> dict:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def serialize_fields(cls):
        raise NotImplementedError

    @property
    def auto_save(self):
        return self._auto_save if hasattr(self, "_auto_save") else False

    @auto_save.setter
    def auto_save(self, x):
        setattr(self, "_auto_save", x)
