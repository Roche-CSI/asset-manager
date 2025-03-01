from server_core.models.asset_settings import AssetSettings
import pytest


@pytest.fixture(scope="module")
def settings_data(test_app):
    """need the test_app fixture for making db transactions"""
    return {
        'default_project': 'asset_playground',
        'server_available': True  # turn to true of false when doing migrations
    }


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "assetsettings" in tables


def test_crud_operations(test_user, settings_data):
    # need the test_app fixture for db operations
    for key in settings_data:

        # create
        record = AssetSettings.create(user=test_user, name=key, value=settings_data.get(key))
        assert record.name == key
        assert record.value == settings_data.get(key)

        # update and read
        record.value = "random_string"
        record.save(user=test_user)
        saved = AssetSettings.get_if_exists(AssetSettings.id == record.id)
        assert saved.value == "random_string"

        # soft delete
        saved.delete_instance(user=test_user)
        soft_del = AssetSettings.get_if_exists(AssetSettings.id == saved.id,
                                               include_deleted_records=True)

        # soft delete records shouldn't be publicly accessible
        public = AssetSettings.get_if_exists(AssetSettings.id == saved.id)
        assert public is None

        # permanent delete
        saved.delete_instance(user=test_user, permanently=True)
        exists = AssetSettings.get_if_exists(AssetSettings.id == saved.id,
                                             include_deleted_records=True)
        assert exists is None
