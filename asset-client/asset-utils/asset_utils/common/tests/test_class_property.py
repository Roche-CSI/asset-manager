from asset_utils.common.class_property import classproperty


def test_class_property():
    class Bar(object):
        _bar = 1

        @classproperty
        def bar(cls):
            return cls._bar

        @bar.setter
        def bar(cls, value):
            cls._bar = value

    # test instance creation
    foo = Bar()
    assert foo.bar == 1

    baz = Bar()
    assert baz.bar == 1

    # classproperty getter
    assert Bar.bar == 1

    # classproperty setter
    Bar.bar = 50
    assert foo.bar == 50
    assert baz.bar == 50
