from asset_utils.utils import rgetattr


def asset_desc(asset):
    desc_keys = [{'name': 'asset'},
                 {'id': 'id'},
                 {'created_at': 'created_at'},
                 {'created_by': 'created_by'},
                 {'latest_version': 'version.number'},
                 {'alias': 'alias'}]

    # heading1 = f"asset: {asset.name}, " + \
    #            f"id: {asset.id}, " + \
    #            f"created_at: {asset.created_at}, " + \
    #            f"created_by: {asset.created_by}, " + \
    #            f"latest_version: {asset.version.number}, " + \
    #            f"alias: {asset.alias}"
    return {key: rgetattr(asset, key) for key in desc_keys}


def asset_class_desc(asset_class):
    heading2 = f"class: {asset_class.name}, " + \
               f"id: {asset_class.id}"
    return heading2
