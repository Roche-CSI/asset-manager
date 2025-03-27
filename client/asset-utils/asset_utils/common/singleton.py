import abc


class Singleton:
    __metaclass__ = abc.ABCMeta

    def __new__(cls):
        raise Exception("singleton, used class.shared() instead")

    @classmethod
    def shared(cls, **kwargs):
        if cls is Singleton:
            raise Exception("abstract class, you must inherit")
        if not hasattr(cls, 'instance') or not getattr(cls, 'instance'):
            instance = super(Singleton, cls).__new__(cls)
            instance.post_init(**kwargs)
            cls.instance = instance
        return cls.instance

    def post_init(self, **kwargs):
        """subclass must implement and do any custom initialization here
        - we do this here to not let users make the mistake of implementing __init__
        - __init__ is called everytime the user tries to instantiate
        the class, even when we override __new__ as obove
        - this is counterintuitive to how we perceive singletons in other languages
        """
        raise NotImplementedError

    @classmethod
    def de_init(cls):
        """
        need a de_init so that we can test different inheritances of the singleton
        :return:
        """
        setattr(cls, 'instance', None)
