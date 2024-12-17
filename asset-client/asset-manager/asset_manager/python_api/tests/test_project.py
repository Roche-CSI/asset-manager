from asset_manager.python_api.project import Project


def test_list():
    project_list = Project().list()
    assert project_list
    expected = ['name', 'id', 'description', 'remote_url', 'is_active']
    for project in project_list:
        for key in expected:
            assert key in project


def test_active_project():
    active = Project().active
    expected = ['name', 'id', 'description', 'remote_url', 'is_active']
    assert type(active) is dict
    for key in expected:
        assert key in active
