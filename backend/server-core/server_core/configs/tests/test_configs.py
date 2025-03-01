import pytest
from asset_client.configs.configs import Configs


@pytest.fixture(scope="module")
def config():
    return Configs.shared(test=True)


def test_instance_creation(config: Configs):
    assert config.bucket_url() == "gs://placeholder_bukcet/tests"
    assert config.bucket_url(staging=True) == "gs://placeholder_bukcet/tests"
    assert config.contents_url(staging=False) == "gs://placeholder_bukcet/tests/contents"
    assert config.contents_url(staging=True) == "gs://placeholder_bukcet/tests/contents_temp"
    assert config.assets_url == 'gs://placeholder_bukcet/tests/assets'


