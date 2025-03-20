import os
from unittest.mock import patch

from asset_core.objects.group.group_object import GroupObject
from asset_core.objects.object import Object
from asset_core.objects.object_factory import ObjectFactory
from asset_plugin_gcr.gcr_storage import GcrStorage
from asset_plugin_gcs.gcs_storage import GcsStorage
from asset_plugin_s3.aws_storage import AwsStorage


def test_bulk_create_posix(empty_asset, test_data):
    factory = ObjectFactory()
    sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[test_data])
    objects = factory.bulk_create(source_data=sources)
    assert len(objects) == 2


def test_bulk_create_gcs(empty_asset, mock_gcs_blob):
    factory = ObjectFactory()
    os.environ["ASSET_PROJECT_STORAGE_ID"] = "gs"
    with patch.object(GcsStorage, 'list_blobs', return_value=[mock_gcs_blob]):
        sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[mock_gcs_blob.url])

    objects = factory.bulk_create(source_data=sources, proxy=True)
    assert len(objects) == 1
    assert type(objects[0]) is Object
    content = objects[0].content
    assert content.id == 'gs:proxy_md5_HHf38PoTxw3ja++ikBY4Vg=='
    assert content.size == 12853831
    assert content.meta.get("proxy") is True
    assert content.meta.get("type") == "gs"
    assert content.meta.get("src") == mock_gcs_blob.url


def test_bulk_create_s3(empty_asset, mock_s3_blob):
    factory = ObjectFactory()
    os.environ["ASSET_PROJECT_STORAGE_ID"] = "s3"
    with patch.object(AwsStorage, 'list_blobs', return_value=[mock_s3_blob]):
        sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[mock_s3_blob.url])

    objects = factory.bulk_create(source_data=sources, proxy=False)
    assert len(objects) == 1
    assert type(objects[0]) is Object
    content = objects[0].content
    assert content.id == 's3:md5_eIlrw2PBTOr3VKXLHClkTQ=='
    assert content.size == 17160
    assert content.meta.get("proxy") is False
    assert content.meta.get("type") == "s3"
    assert content.meta.get("src") == mock_s3_blob.url


def test_bulk_create_gcr(empty_asset, mock_gcr_blob):
    factory = ObjectFactory()
    os.environ["ASSET_PROJECT_STORAGE_ID"] = "gs"
    with patch.object(GcrStorage, 'list_blobs', return_value=[mock_gcr_blob]):
        sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[mock_gcr_blob.url])

    objects = factory.bulk_create(source_data=sources, proxy=True)
    assert len(objects) == 1
    assert type(objects[0]) is Object
    content = objects[0].content
    assert content.id == 'gcr:proxy_md5_YQ4XfTQ0xDljPZuNX2uLzQ=='
    assert content.size == 2391153464
    assert content.meta.get("proxy") is True
    assert content.meta.get("type") == "gcr"
    assert content.meta.get("src") == mock_gcr_blob.url


def test_get_object_class():
    factory = ObjectFactory()
    assert factory.get_object_class('group') == GroupObject
    assert factory.get_object_class() == Object


def test_object_klasses():
    assert ObjectFactory().object_klasses() == [Object, GroupObject]


def test_create_contents(empty_asset, test_data):
    factory = ObjectFactory()
    sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[test_data])
    contents = factory.create_contents(source_data=sources)
    assert len(contents) == 2


def test_parse_sources_posix(empty_asset, test_data):
    factory = ObjectFactory()
    sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[test_data])
    assert len(sources) == 1
    assert len(sources['posix']) == 2


def test_parse_sources_gcs(empty_asset, mock_gcs_blob):
    factory = ObjectFactory()
    with patch.object(GcsStorage, 'list_blobs', return_value=[mock_gcs_blob]):
        sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[mock_gcs_blob.url])
        assert len(sources) == 1
        assert len(sources['gs']) == 1
        source = sources['gs'].pop()
        assert source.path_in_asset == 'photo-1522364723953-452d3431c267.jpg'


def test_parse_sources_s3(empty_asset, mock_s3_blob):
    factory = ObjectFactory()
    with patch.object(AwsStorage, 'list_blobs', return_value=[mock_s3_blob]):
        sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[mock_s3_blob.url])
        assert len(sources) == 1
        assert len(sources['s3']) == 1
        source = sources['s3'].pop()
        assert source.path_in_asset == 'customers.csv'


def test_parse_sources_gcr(empty_asset, mock_gcr_blob):
    factory = ObjectFactory()
    with patch.object(GcrStorage, 'list_blobs', return_value=[mock_gcr_blob]):
        sources = factory.parse_sources(repo_dir=empty_asset.repo_dir, targets=[mock_gcr_blob.url])
        assert len(sources) == 1
        assert len(sources['gcr']) == 1
        source = sources['gcr'].pop()
        assert source.path_in_asset == 'my-test-project-my-test-image-sha256-1234567890abcdef1234567890abcdef1234567890abcdef1234567890'
