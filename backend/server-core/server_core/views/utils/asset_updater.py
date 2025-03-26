import copy

from asset_utils.common import exceptions
from asset_utils.utils import is_integer, contains_special_chars
from flask import current_app

from server_core.elastic.asset_entry import AssetEntry
from server_core.elastic.vector_search import ElasticVectorSearch
from server_core.models.asset import Asset
from server_core.models.base.base import db_proxy as db

TEMP_SEQ_PREFIX = "temp_"
MAX_ALLOWED_TAGS = 10
MAX_TAG_LENGTH = 20


def update_asset_record(asset: Asset, data: dict) -> dict:
    """Validates and updates fields of an asset

    Fields available for update:
    - frozen
    - title
    - description
    - metadata
    - attributes
    - phase
    - alias
    - tags

    Make sure to update the asset in one single transaction.
    If error occurs, exception would be raised and no updates will be made to the asset.

    Returns
    -------
    dict
        updated asset data

    Raises
    ------
    AssetException
        if any error occurs during the update
    """
    updates = []
    # make a copy of the asset for rollback
    previous_asset = copy.deepcopy(asset)

    if "frozen" in data:
        asset.frozen = data.get("frozen")
        updates.append(Asset.frozen)
    if "title" in data:
        asset.title = data.get("title")
        updates.append(Asset.title)
    if "description" in data:
        asset.description = data.get("description")
        updates.append(Asset.description)
    if "metadata" in data:
        asset.metadata = data.get("metadata")
        updates.append(Asset.metadata)
    if "attributes" in data:
        asset.attributes = data.get("attributes")
        updates.append(Asset.attributes)
    if "phase" in data:
        asset.phase = data.get("phase")
        updates.append(Asset.phase)
    if "status" in data:
        asset.status = data.get("status")
        updates.append(Asset.status)

    if "alias" in data:
        alias = data.get("alias")
        # remove leading and trailing whitespaces
        alias = alias.strip() if alias else None
        if not alias:  # removing alias
            # convert both None and empty string to None
            asset.alias = None
            updates.append(Asset.alias)
        else:  # adding alias
            existing = Asset.get_if_exists(Asset.asset_class == asset.asset_class,
                                           Asset.alias == alias)
            # check if other assets from the same class has the same alias
            if existing and existing.id != asset.id:
                raise exceptions.InvalidAliasError(
                    f"another asset with alias: {alias} already exists in class: {asset.asset_class.name}")
            else:
                validate_alias(alias)
                asset.alias = data.get("alias")
                updates.append(Asset.alias)

    if "tags" in data:
        # remove leading and trailing whitespaces
        tags = [tag.strip() for tag in data.get("tags")]
        # remove duplicates
        tags = set(tags)
        for tag in tags:
            validate_tag(tag)
        # check if the number of tags exceeds the limit
        if len(tags) > MAX_ALLOWED_TAGS:
            raise exceptions.InvalidTagError(f"a maximum of {MAX_ALLOWED_TAGS} tags is allowed")
        # update the asset tags
        asset.tags = list(tags)
        updates.append(Asset.tags)

    if updates:
        if has_search_engine():
            try:
                # add to elastic-search index, will rollback if error occurs later
                update_elastic(asset=asset, updates=updates, user=data["user"])
            except Exception as e:
                raise exceptions.AssetException(f"failed to update elastic search index: {e}")

        # use atomic transaction so db doesn't get updated if error occurs
        with db.atomic():
            try:
                # write to database
                asset.save(only=updates, user=data["user"])
                # write to bucket
                asset.write_to_bucket(alias=bool("alias" in data))
            except Exception as e:
                # rollback elastic search index
                update_elastic(asset=previous_asset, updates=updates, user=data["user"])
                raise exceptions.AssetException(f"failed to update asset: {e}")

    return asset.to_dict()


def has_search_engine():
    return hasattr(current_app, 'search_engine') and current_app.search_engine is not None


def update_elastic(asset: Asset, updates: list, user: str):
    # check if updates include elastic fields
    includes = False
    elastic_fields = ["title", "description", "tags", "alias", "metadata"]
    for field in updates:
        if field in elastic_fields:
            includes = True
            break

    if not includes:
        return

    search: ElasticVectorSearch = current_app.search_engine
    if not search:
        print("elastic search engine not available - skipping index updating")
        return

    asset_class = asset.asset_class
    project = asset_class.project

    entry = AssetEntry.create(asset=asset,
                              class_name=asset_class.name,
                              class_id=str(asset_class.id),
                              class_title=asset_class.title,
                              class_status=asset_class.status,
                              class_type=asset_class.class_type,
                              project_name=project.name,
                              project_title=project.title,
                              project_id=str(project.id),
                              project_status=project.status,
                              es_score=None,
                              es_highlight=None,
                              )
    updated = entry.upsert(es=search, user=user)
    print(f"updated elastic search index: {updated}")


def validate_alias(alias: str) -> None:
    """Validates the alias for the asset."""
    if not alias:
        raise exceptions.InvalidAliasError("missing alias")
    # must not be an integer
    if is_integer(alias):
        raise exceptions.InvalidAliasError("alias cannot be an integer")
    if type(alias) is not str:
        raise exceptions.InvalidAliasError("alias must be a string")
    if contains_special_chars(alias):
        raise exceptions.InvalidAliasError("alias cannot contain any special characters other than '_', '.', '-'")
    # validate that it doesn't start with TEMP_SEQ_PREFIX
    if alias.startswith(TEMP_SEQ_PREFIX):
        raise exceptions.InvalidAliasError(f"alias cannot start with: {TEMP_SEQ_PREFIX}")


def validate_tag(tag: str) -> None:
    """Checks if the tag is valid.
    - max len 20 chars
    - only lowercase and digits
    - not integer or float
    - no special chars except '_', '.', '-'
    """
    if not tag:
        raise exceptions.InvalidTagError("missing tag")
    if len(tag) > MAX_TAG_LENGTH:
        raise exceptions.InvalidTagError("tag length must be less than 20 characters")
    if not tag.islower():
        raise exceptions.InvalidTagError("tag must be in lowercase")
    if is_integer(tag):
        raise exceptions.InvalidTagError("tag cannot be an integer")
    if contains_special_chars(tag):
        raise exceptions.InvalidTagError("tag cannot contain any special characters other than '_', '.', '-'")
