import logging
import os

from flask import Blueprint, Response, request
from packaging import version

from server_core import models
from server_core.asset_client.asset_writer import AssetWriter
from server_core.models.asset import Asset as AssetModel
from server_core.utils import time_it
from server_core.utils.json_encoder import to_json
from server_core.views.utils.asset_commit import AssetCommit, CommitData
from server_core.views.utils.view_utils import data_from_request

logger = logging.getLogger(__file__)

asset_commit_view = Blueprint(name='asset_commit_view', import_name=__name__)


@asset_commit_view.route('', methods=['GET', ])
def list_assets():
    result = [AssetWriter().retrieve_from_db(asset) for asset in AssetModel.public()]
    return Response(to_json(result), mimetype="application/json", status=200)


@asset_commit_view.route('/<id>', methods=['GET', 'PUT'])
def get_update_asset(id: str):
    if request.method == "PUT":
        data = data_from_request(request)
        return commit_asset(user=data.get("user"),
                            data=data.get("payload"),
                            message=data.get("message"),
                            bucket_sync=data.get("bucket_sync", True)
                            )
    else:
        asset = AssetModel.get_if_exists(AssetModel.id == id)
        return Response(to_json(AssetWriter().retrieve_from_db(asset)), mimetype="application/json", status=200)


def commit_asset(user, data, message=None, bucket_sync=True):
    """
    To ensure atomicity, we need to make sure the asset being committed isn't already committed.
    To verify, check if the asset has a commit-hash already. If it does, then send the message back to the
    asset-client that this asset has been committed and can't be modified.

    The client upon receiving the response, should flag the asset as committed, and send a request again for
    creating a new asset but with the same parent. The server will then create the asset record and send a new id.
    After receiving the id, the client will reinitiate the commit process

    Parameters
    ----------

    Returns
    -------

    """
    is_valid, error = validate(data=data)
    if not is_valid:
        return Response(to_json({"error": error}), mimetype="application/json", status=400)

    class_data: dict = data.get("asset_class", {})
    if not class_data.get("project"):
        raise Exception("missing required parameters: project")
    project = models.Project.get_if_exists(models.Project.id == class_data.get("project"))
    if not project:
        raise Exception("missing required parameters: project")

    with project.storage(server=True):
        # asset.commit_contents()
        writer = AssetCommit(username=user, data=data)
        with time_it("db-save"):
            saved: CommitData = writer.save_to_db()
        if bucket_sync:
            with time_it("yamlize"):
                saved.serialize()
            with time_it("bucket-save"):
                saved.write_to_bucket(storage_url=os.environ["remote_url"])
                saved.update_object_rels()

    return Response(to_json(saved.json_data), mimetype="application/json", status=200)


def validate(data: dict) -> tuple:
    """validates request from asset-client

    Parameters
    ----------
    data: request data

    Returns
    -------
    tuple: validation result, error message

    """
    # check if server is available
    if not models.AssetSettings.server_available():
        return False, "asset-server not available, critical maintenance ongoing"

    # check if the cli-version is supported
    cli_version = data.pop("cli_version", None)
    if not cli_version:
        # note: this is temp, raising exception to force asset-client to upgrade to 2.0
        raise Exception("missing required param: cli-version, asset-client needs upgrade")
        # return False, "missing required param: cli_version"

    supported_cli_version = models.AssetSettings.supported_cli_version()
    if not supported_cli_version:
        return False, "server must have a supported CLI version"

    if version.parse(cli_version) < version.parse(supported_cli_version):
        return False, f"unsupported cli-version, you must have a cli-version:{supported_cli_version} or greater"

    return True, None
