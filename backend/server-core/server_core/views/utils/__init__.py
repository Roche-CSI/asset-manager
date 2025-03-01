from server_core import models
# pluggy--
from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage


def signed_url_for_content(content: models.Content, class_id: str):
    if not content.can_download():
        return None
    # get the project
    class_record = models.AssetClass.get_if_exists(models.AssetClass.id == class_id)
    if not class_record:
        raise Exception("invalid asset-class:{}".format(class_id))
    project: models.Project = class_record.project
    with project.storage():
        content_url = content.read_url(class_id=class_id)
        asset_storage: AssetStorage = StorageFactory.storage_for_url(content_url)
        signed_url = asset_storage.signed_url_for_blob(blob_url=content_url)
        # bucket, blob_name = parse_gcp_url()
        # signed_url = generate_signed_url(
        #     service_account_json=Configs.shared().storage_credentials,
        #     bucket_name=bucket,
        #     object_name=blob_name
        # )
        return signed_url
