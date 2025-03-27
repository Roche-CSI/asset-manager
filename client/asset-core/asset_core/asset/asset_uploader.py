import os

from asset_contents.content_uploader import ContentUploader
from asset_core.asset import AssetClass, Asset
from asset_core.asset.asset_diff import AssetDiff
from asset_core.asset.asset_snapshot import AssetSnapshot
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.asset.status_enums import StatusEnums
from asset_core.configs import AppSettings
from asset_core.server import AssetServer
from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from asset_pluggy.storage.transporter import TransportResource
from asset_utils.common import exceptions
from asset_utils.utils.cloud_utils import internet_on
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LogColors
from asset_utils.utils.log_utils import LoggingMixin
from asset_utils.utils.progress import Progress


class AssetUploader(LoggingMixin):
    asset: Asset = None

    def __init__(self, asset):
        self.asset = asset

    def upload_asset(self,
                     freeze: bool = False,
                     commit_msg: str = None):
        """Uploads asset to remote.
        The order of upload operations is important for ensuring atomicity and resummable transaction
        in the event of interruptions.
        1. If there are refs that need verification (user may have added refs while being offline),
        we verify those first. Its important for two reasons,
        - first: we can inform the user of any errors, i.e. mistyped names or referencing a non existing asset etc,
        since upload could take a lot of time, we want to make sure transaction errors are caught as early as possible
        - second: the refs are integral to commit, so we make sure that the refs are accurate and wrongly
        referenced commit is not created
        The reason why can't create the refs in this stage is because that commit doesn't exist yet

        2. if there are contents to upload, we upload the contents to staging bucket (this is the most time-consuming part of the operations).
        A version can only be committed by the server - once all data is accurately available in remote.
        3. Commit the asset using server i.e. update its version
        4. Update asset alias. Its important to make a note here - it might be tempting to update the
        alias at the beginning and the server commit flow will work fine. But this flow breaks the following
        controls:
        - If an asset is created upfront, its no longer a temp asset. Lets say, the alias is updated successfully
        but the commit flow breaks because of network issue, we are left with a dangling asset in local that
        is no longer temporary but at the same time doesn't have a version. This will have ripple effects to
        how caching and versioning (staging /unstaging /diff /undo/ redo) works. Since these operations assume
        that every remote asset will have atleast a root version.
        5. update refs: update the references to the asset version. The order of ref update and alias changes
        are interchangeable and will not cause issues. Note: Its possible that we combine asset-commit with update-refs
        and it will work fine for most parts. Perhaps would be better for atomicity since refs and commits would be
        created in the same transaction. However this breaks the flow of adding refs after a commit since a user
        may have missed to add a ref while committing or may have added a wrong ref, this is why the update-ref
        has been kept independent of asset-commit

        """
        if not self.can_upload():
            return

        # keep the seq_id, we need it to determine if it was a temp or not
        seq_id = self.asset.seq_id
        # upload contents (version will be updated)
        committed = self.commit_asset() if self.upload_contents(commit_msg=commit_msg) else None
        # update asset refs and aliases if any (no version update)
        updated = self.update_asset_record(seq_id, freeze=freeze)
        did_upload = bool(updated or committed)
        if did_upload:
            message = "success\n"
            message += "asset upload complete\n"
            message += f"updated version: {self.asset.version.number}"
            self.user_log.success(message)
        else:
            self.user_log.info("asset is clean, there is nothing to commit")
            self.user_log.message("please add files, inputs, or alias to asset in order to commit")

    def ask_user_for_commit(self, existing_msg: str = None):
        message = f"commit-message: {existing_msg or 'missing'}, proceed?"
        user_input = self.user_log.ask_user(question=message,
                                            options=['<new-message + enter>', '<enter>'],
                                            default="")
        return user_input or existing_msg

    def can_upload(self):
        # missing storage credentials
        if not StorageCredentials.shared().credentials:
            raise exceptions.InvalidCredentialError("missing storage credentials")

        # user has not added any files
        # note: we do this only for first commit, since user can remove files in a later version
        if self.asset.is_temp and len(self.asset.objects) == 0:
            self.user_log.info("asset is empty, there is nothing to commit")
            return False

        # check linking type
        if self.asset.repo.linking_type != "copy":
            raise exceptions.ReadOnlyAssetError(
                f"read-only asset, change tracking and updates are disabled: {self.asset.repo.linking_type}")

        if not self.verify_refs():
            return False

        # todo: add alias verification here to avoid duplicate alias error.
        #  we want to alert the user right at the beginning

        # check status and raise exceptions
        self.verify_status()

        return True

    def verify_status(self):
        """Verifies the status of the asset_clas and asset before uploading."""
        fetcher = AssetFetcher(store=self.asset.repo.store)
        # fetch the latest asset-class data
        fetcher.download_asset_class(class_id=self.asset.asset_class.id)
        class_data = AssetClass.cached_class_data(store=fetcher.store, id=self.asset.asset_class.id)
        self.asset.asset_class.de_serialize(asset=self.asset, data=class_data)

        if not self.asset.is_temp:
            # fetch the latest asset data
            file = fetcher.download_asset_file(class_id=self.asset.asset_class.id, seq_id=str(self.asset.seq_id))
            # update the asset list with the latest asset
            self._update_asset_list(fetcher=fetcher)
            asset_data = FileUtils.read_yaml(file)
            if asset_data.get("status"):
                self.asset.status = asset_data.get("status")

        try:
            StatusEnums.can_upload(asset=self.asset)
        except exceptions.AssetException:
            # update asset manifest file if not temp asset (not the cached manifest)
            if not self.asset.is_temp:
                self.asset.save()
            raise

    def verify_refs(self):
        """Verifies if the added refs have any errors that would cause errors while
        creating ref records in the database. One such error could be invalid asset name.
        We do the verification at the beginning of the upload to ensure atomicity and also alert users
        of any possible errors as soon as possible.

        Typically, refs are verified at the time of adding, however its possible the user was offline
        at the time of adding refs, so we delegate the verification to at the time of upload
        """
        if self.asset.refs.is_verified():
            return True
        else:
            return self.asset.refs.verify_ref_sources()

    def commit_asset(self):
        if self.asset.view != Asset.views.RAW:
            raise exceptions.AssetException("invalid operation, required mode is RAW")

        prev_version = self.asset.version.number
        prev_seq = self.asset.seq_id
        # hand-off to server for commit
        saved = self._commit_to_server()

        # update version and seq_id
        self.asset.seq_id = saved.get("seq_id")
        self.asset.version.de_serialize(asset=self.asset, data=saved.get("version"))
        self.asset.asset_class.de_serialize(asset=self.asset, data=saved.get("asset_class"))
        # since we updated the version, this will save to a new file
        self.asset.save()

        serialized = saved

        # update states
        # content states
        for content in self.asset.contents:
            content.set_state(content.states.COMMITTED)
        # bulk update
        self.asset.contents.update_states(self.asset.contents, save=True)

        # object states
        for obj in self.asset.objects:
            obj.set_state(obj.states.COMMITTED)
        self.asset.objects.update_states(self.asset.objects, save=True)

        # asset state
        self.asset.set_state(self.asset.states.COMMITTED, save=True)

        # get the updated asset metadata into the asset store
        self._update_asset_metadata()

        # cleanup previous version
        if serialized:
            self.cleanup_previous_version(prev_version=prev_version)
            # update version in repo
            self.asset.set_as_current()
            # update the repo for version and seq_id
            self.asset.set_as_current()
            # remove from temp assets
            if Asset.is_temp_seq_id(prev_seq):
                self.asset.repo.remove_from_temp_assets(seq_id=prev_seq,
                                                        class_name=self.asset.asset_class.name)
            # reset the commit message
            self.asset.commit_message = None

        return serialized

    def _commit_to_server(self):
        """Commits the asset to the server."""
        serialized = self.asset.serialize()
        serialized["objects"] = [obj.serialize() for obj in self.asset.objects]
        serialized["cli_version"] = AppSettings.shared().cli_version
        # update version size
        serialized["version"]["size"] = self.asset.objects.size

        try:
            saved, status = AssetServer().commit_asset(id=self.asset.id,
                                                       data=serialized,
                                                       message=self.asset.commit_message)
        except exceptions.ServerNotAvailableError as e:
            # connection error, we need to check if internet or server
            if not internet_on():
                message = "Unable to connect, make sure you are connected to internet"
            else:
                message = "Asset Server not available. You need to be connected to Roche VPN to access the server."
            e.logs.add(message, LogColors.ALERT)
            raise
        except exceptions.AssetException as e:
            e.logs.add("unable to commit asset", LogColors.ERROR)
            raise

        if status != 200:
            raise exceptions.AssetException(
                f"unable to commit-asset, asset-server rejected the transaction: {saved.get('error')}")

        if not saved or not saved.get("seq_id"):
            raise exceptions.AssetException("unable to commit asset, asset-server rejected the transaction")

        return saved

    def _update_asset_metadata(self):
        """Update asset metadata on the asset store.

        - an object snapshot file (depending on the version)
        - get the version_*.yaml files from last snapshot to the current version
        - update the objects_v2 directory
        - create the cached manifest file for the new version
        """
        asset_snapshot = AssetSnapshot(store=self.asset.repo.store)
        latest_snapshot = asset_snapshot.latest_remote_snapshot(class_id=self.asset.asset_class.id,
                                                                seq_id=str(self.asset.seq_id),
                                                                version=self.asset.version.number)
        # download the latest snapshot file if it exists
        if latest_snapshot:
            asset_snapshot.download(class_id=self.asset.asset_class.id,
                                    seq_id=str(self.asset.seq_id),
                                    version=latest_snapshot)

        fetcher = AssetFetcher(store=self.asset.repo.store)
        # download the necessary version yaml files
        fetcher.download_snapshot_versions(class_id=self.asset.asset_class.id,
                                           seq_id=str(self.asset.seq_id),
                                           snapshot_version=latest_snapshot,
                                           target_version=self.asset.version.number)

        # update the objects_v2 directory
        fetcher.download_asset_objects(class_id=self.asset.asset_class.id,
                                       seq_id=str(self.asset.seq_id),
                                       show_progress=True)

        # create the cached manifest file for the new version
        AssetDiff().create_cached_manifest_file(asset=self.asset)

    def cleanup_previous_version(self, prev_version):
        # cleanup the previous version
        # delete the manifest and state files, they will be recreated when needed
        FileUtils.delete_file(Asset.manifest_path(repo=self.asset.repo,
                                                  asset_id=self.asset.id,
                                                  version=prev_version))
        FileUtils.delete_file(Asset.states_path(repo=self.asset.repo,
                                                asset_id=self.asset.id,
                                                version=prev_version))

    def update_asset_record(self, seq_id, freeze=False) -> bool:
        """Updates the asset for any changes in asset records or refs."""
        record_changes = self._asset_record_changes(seq_id=seq_id, asset=self.asset)
        if record_changes or freeze:
            if not self.asset.version.commit_hash:
                raise exceptions.AssetException("asset doesn't have any commits, can't be uploaded")

            # push the asset changes to the server and the asset.yaml file
            self.user_log.info("updating asset records")
            response = AssetServer().update_asset(id=self.asset.id, data={**record_changes, "frozen": freeze})
            if response.get("error"):
                # server sends back error message for unsuccessful operations such as duplicate alias etc
                raise exceptions.IncorrectServerResponseError(f"unable to update asset: {response.get('error')}")
            # users might have updated these records through asset-dashboard
            # so always update the asset records with the response data
            self.asset.seq_id = response.get("seq_id")  # this will autosave
            self.asset.alias = response.get("alias")  # this will autosave
            self.asset.title = response.get("title")
            self.asset.description = response.get("description")
            self.asset.tags = response.get("tags")
            self.asset.metadata = response.get("metadata")
            self.asset.attributes = response.get("attributes")
            self.asset.frozen = response.get("frozen")

        # check for updates to the asset refs
        self.asset.refs.update_temp_refs()
        refs_added, refs_removed = self.asset.refs.ref_changes()
        if refs_added or refs_removed:
            self.user_log.info("updating asset inputs")
            response = self._update_asset_inputs(added=refs_added, removed=refs_removed)
            # make sure response contains all references to the asset
            self.asset.refs.clear(save=True)
            self.asset.refs.de_serialize(data=response)
            self.asset.refs.save()  # we need to save explicitly for refs
        else:
            # flag the ref states to committed
            self.user_log.info("updating states of asset inputs")
            for ref in self.asset.refs:
                if ref.get_state() != ref.states.COMMITTED:
                    ref.set_state(ref.states.COMMITTED, save=True)

        asset_updated = bool(refs_added or refs_removed or record_changes)
        if asset_updated:
            fetcher = AssetFetcher(self.asset.repo.store)
            # update the asset.yaml file
            fetcher.download_asset_file(class_id=self.asset.asset_class.id, seq_id=str(self.asset.seq_id))
            # update the asset_list.yaml for the asset class
            self._update_asset_list(fetcher=fetcher)
            # update the asset manifest file in asset store
            AssetDiff().create_cached_manifest_file(asset=self.asset, force=True)

        return asset_updated

    def _update_asset_list(self, fetcher: AssetFetcher) -> None:
        """Updates the asset_list.yaml for the asset class."""
        pbar = Progress.status_bar(desc=f"constructing asset list for class: {self.asset.asset_class.name}")
        fetcher.create_asset_list_for_class(self.asset.asset_class)
        pbar.close("done")

    def _update_asset_inputs(self, added: list, removed: list):
        """Updates the asset inputs on the server and prints updates."""
        add_data = [
            {
                "src_version": item.get('src_version').get('id'),
                "dst_version": item.get('dst_version').get('id'),
                "label": item.get("label"),
                "properties": item.get("properties")
            } for item in added]
        remove_data = [
            {
                "id": item.get('id'),
                "src_version": item.get('src_version').get('id'),
                "dst_version": item.get('dst_version').get('id')
            } for item in removed]

        # update the asset inputs on the server
        response = AssetServer().update_refs({"added": add_data, "removed": remove_data})
        if "error" in response:
            raise exceptions.AssetException(f"unable to update inputs: {response.get('error')}")

        # print the inputs updates
        if added:
            updated_inputs = [item['src_version']['name'] for item in added]
            self.user_log.message(f"added inputs: {', '.join(updated_inputs)}")
        if removed:
            updated_inputs = [item['src_version']['name'] for item in removed]
            self.user_log.message(f"removed inputs: {', '.join(updated_inputs)}")

        return response

    def _asset_record_changes(self, seq_id, asset: Asset) -> dict:
        """Check and track the asset records changes.
        - alias
        - title
        - description
        """
        changes = {}
        if Asset.is_temp_seq_id(seq_id):
            # local asset so check if records are set
            if asset.alias:
                changes["alias"] = asset.alias
            if asset.title:
                changes["title"] = asset.title
            if asset.description:
                changes["description"] = asset.description
            if asset.metadata:
                changes["metadata"] = asset.metadata
            if asset.attributes:
                changes["attributes"] = asset.attributes
            if asset.tags:
                changes["tags"] = asset.tags
        else:
            # compare with cache to find any changes
            previous = self.asset.cached_asset_data() or {}
            if previous.get("alias") != asset.alias:
                changes["alias"] = asset.alias
            if previous.get("title") != asset.title:
                changes["title"] = asset.title
            if previous.get("description") != asset.description:
                changes["description"] = asset.description
            if previous.get("metadata") != asset.metadata:
                changes["metadata"] = asset.metadata
            if previous.get("attributes") != asset.attributes:
                changes["attributes"] = asset.attributes
            if set(previous.get("tags", [])) != set(asset.tags or []):
                changes["tags"] = asset.tags

        return changes

    def upload_contents(self, commit_msg: str = None):
        if self.asset.view != self.asset.views.RAW:
            raise exceptions.AssetException("asset can only be uploaded in raw mode")

        if len(self.asset.objects) == 0:
            return False

        # check if state has changed
        # if self.asset.get_state() and self.asset.get_state() != self.asset.states.PENDING:
        if not self.asset.can_commit():
            # no changes to commit
            return False

        # we need the top hash, update if not exists
        if not self.asset.top_hash:
            self.asset.asset_class.id = self.asset.asset_class.id or self.init_asset_class(self.asset)
            self.asset.top_hash = self.asset.asset_class.id

        current_hash = self.asset.objects.hash
        if current_hash == self.asset.version.commit_hash:  # previous hash
            # this means, user did delete/add, which is a state change but not a version change
            # so we reset the states
            self._flag_as_committed(asset=self.asset)
            self.user_log.info("There are no file changes to commit")
            return False
        else:
            # if no commit message, ask user
            commit_msg = commit_msg or self.asset.commit_message
            if not commit_msg:
                # ask user to confirm, if there was a previous unsuccessful upload
                commit_msg = self.ask_user_for_commit(existing_msg=self.asset.commit_message)
            self.user_log.info(f"uploading commit: {current_hash} - '{commit_msg}'")
            # there are changes that need to be updated
            # could be additions, deletions or both
            # 1. upload data-view contents
            self._upload_dataview_contents(asset=self.asset.deep_copy(view=Asset.views.DATA))
            # 2. upload raw-view contents
            self._upload_raw_view_contents(asset=self.asset, current_hash=current_hash, commit_msg=commit_msg)
            return True

    def _upload_dataview_contents(self, asset: Asset):
        if asset.view != Asset.views.DATA:
            raise exceptions.AssetException("invalid operation for asset, required mode is DATA")

        if len(asset.objects.items) == 0:
            return

        # check if state has changed
        # if self.asset.get_state() and self.asset.get_state() != self.asset.states.PENDING:
        if not asset.can_commit():
            # no changes to commit
            return

        self.user_log.info("uploading derived contents")
        # there are changes that need to be updated
        # could be additions, deletions or both
        staged = ContentUploader(asset.contents).upload_to_remote()
        # update states
        if staged:
            for content in staged:
                content.set_state(content.states.COMMITTING, save=True)
            # bulk update
            asset.contents.update_states(staged, save=True)

    def _upload_raw_view_contents(self,
                                  asset: Asset,
                                  current_hash: str,
                                  commit_msg: str):
        if asset.view != Asset.views.RAW:
            raise exceptions.AssetException("invalid operation for asset, required mode is RAW")

        uploaded = ContentUploader(asset.contents).upload_to_remote()
        # update states of uploaded contents
        self._flag_as_committing(asset=asset, staged=uploaded, commit_hash=current_hash, commit_msg=commit_msg)

    def _flag_as_committed(self, asset: Asset):
        if asset.view != asset.views.RAW:
            raise exceptions.AssetException("asset state can only be altered in RAW mode")

        # asset
        asset.set_state(self.asset.states.COMMITTED, save=True)
        # objects, do a group update
        target_objects = self.asset.objects.filter(predicate=lambda x: x.can_commit)
        for obj in target_objects:
            obj.set_state(obj.states.COMMITTED)
        asset.objects.update_states(target_objects, save=True)
        # contents also group update
        target_contents = self.asset.contents.filter(predicate=lambda x: x.can_stage)
        for content in target_contents:
            content.set_state(content.states.COMMITTED)
        asset.contents.update_states(target_contents, save=True)

        # update asset state
        asset.set_state(self.asset.states.COMMITTED, save=True)

    def _flag_as_committing(self,
                            asset: Asset,
                            staged: list,
                            commit_hash: str,
                            commit_msg: str):
        if staged:
            for content in staged:
                content.set_state(content.states.COMMITTING, save=True)
            # bulk update
            asset.contents.update_states(staged, save=True)

        # we need to check all objects, because it could be a removal of object,
        # which doesn't reflect in states_db
        target_objects = asset.objects.filter(predicate=lambda x: x.can_commit)
        for obj in target_objects:
            obj.set_state(obj.states.COMMITTING)

        asset.objects.update_states(target_objects, save=True)  # bulk update
        asset.set_state(self.asset.states.COMMITTING, save=True)
        asset.version.commit_hash = commit_hash
        asset.version.commit_message = commit_msg
        asset.commit_message = commit_msg

    def init_asset_class(self, asset) -> str:
        """Create asset class if not exists"""
        self.user_log.info("creating asset class:{}".format(asset.asset_class.name))
        if not asset.asset_class.project:
            raise exceptions.NoActiveProjectError()
        res = AssetServer().create_asset_class(class_name=asset.asset_class.name,
                                               project=asset.asset_class.project)
        # save to local
        FileUtils.write_yaml(abs_path=asset.repo.store.asset_class_file(res.get("id")), data=res)
        return res.get("id")

    def init_asset(self, asset):
        self.user_log.info("creating a new asset for class:{}".format(asset.asset_class.name))
        res = AssetServer().create_asset(**{
            "class_id": asset.asset_class.id,
            "parent": asset.parent
        })
        return {"id": res.get("id"), "version": res.get("version")}

    def upload_object(self, file: str, dst_url: str):
        base_file_name = os.path.basename(file)
        storage = StorageFactory.storage_for_url(src_url=dst_url)
        transporter = storage.get_transporter()
        resource = transporter.get_upload_resource(src=file,
                                                   dst=os.path.join(dst_url, base_file_name),
                                                   src_hash=tuple())
        self.perform_upload(targets=[resource],
                            storage=storage,
                            progress=f"uploading {base_file_name}")

    def perform_upload(self,
                       targets: [TransportResource],
                       storage: AssetStorage,
                       progress: str = None):
        """
        maintaining similar signature as perform_copy(), perform_download() from fetcher
        TODO: refactor asset_uploader.py and content_uploader.py to use this method
        """
        pbar = Progress.progress_bar(total=len(targets), desc=progress) if progress else None
        transporter = storage.get_transporter()
        if pbar:
            for resource in targets:
                resource.callback = lambda x: pbar.update(1)
        try:
            transporter.upload(resources=targets)
            if pbar:
                pbar.close("done")
        except Exception:
            if pbar:
                pbar.close(self.user_log.error("failed"))
            raise
