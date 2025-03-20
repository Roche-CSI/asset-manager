import abc


class AssetObject(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError
