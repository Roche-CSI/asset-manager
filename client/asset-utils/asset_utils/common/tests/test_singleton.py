from asset_utils.common.singleton import Singleton


class SingletonChild(Singleton):
    def post_init(self):
        pass


class SingletonChild2(Singleton):
    def post_init(self):
        pass


def test_singleton():
    child = SingletonChild.shared()
    child_copy = SingletonChild.shared()
    child2 = SingletonChild2.shared()
    child2_copy = SingletonChild2.shared()
    assert child == child_copy
    assert child2 == child2_copy
    assert child != child2
    assert child.__class__ is SingletonChild
    assert child2.__class__ is SingletonChild2
