from asset_pluggy.storage.storage_credentials import StorageCredentials


def test_credentials_property():
    storage_credentials = StorageCredentials.shared()
    content_credentials = {"user": "content_user", "password": "test123"}
    project_credentials = {"user": "project_user", "password": "admin123"}
    # set both content and project credentials
    storage_credentials.set_content_credentials(content_credentials)
    storage_credentials.set_credentials(project_credentials)
    # check both credentials
    assert storage_credentials.credentials == project_credentials
    storage_credentials.use_content_credentials = True
    assert storage_credentials.credentials == content_credentials
