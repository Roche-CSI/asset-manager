from asset_manager.python_api.klass import Klass


def test_list():
    klass = Klass()
    class_list = klass.list()
    assert class_list and type(class_list) is dict


def test_info():
    klass = Klass()
    class_info = klass.info(class_name="swarup_data")
    assert type(class_info) is dict
    expected = ["name", "id", "created_at", "created_by", "class_type", "project"]
    for key in expected:
        assert key in class_info
