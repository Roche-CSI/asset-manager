import os
from typing import List

from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from asset_utils.utils.log_utils import LoggingMixin
from asset_utils.utils.progress import Progress
from .content import Content
from .content_set import ContentSet


class ContentUploader(LoggingMixin):
    contents: ContentSet = None

    def __init__(self, contents):
        self.contents = contents

    def upload_to_remote(self) -> List[Content]:
        """Uploads the contents to remote storage"""
        targets = self.contents.filter(predicate=lambda x: x.can_stage)
        if not targets:
            return []

        copy_targets, upload_targets = [], []
        for content in targets:
            if content.cache_path and os.path.exists(content.cache_path):
                upload_targets.append(content)
            else:
                copy_targets.append(content)

        storage = StorageFactory.storage_for_url(src_url=self.contents.remote_url)
        local_content = self._not_uploaded(targets=targets, storage=storage)
        if len(local_content) == 0:
            return []

        pbar = Progress.progress_bar(desc="uploading files", total=len(local_content))
        upload_targets, copy_targets = [], []
        transporter = storage.get_transporter()
        for content in local_content:
            # nothing to do if content can't be staged i.e. proxy content
            if not content.can_stage:
                continue
            if content.can_upload:
                res = transporter.get_upload_resource(
                    src=content.cache_path,
                    dst=content.remote_url,
                    src_hash=(content.hash_type, content.hash_value)
                )
                res.callback = lambda x: pbar.update(1)
                upload_targets.append(res)
            else:
                res = transporter.get_copy_resource(
                    src=content.source_url,
                    dst=content.remote_url,
                    src_hash=(content.hash_type, content.hash_value),
                )
                res.callback = lambda x: pbar.update(1)
                copy_targets.append(res)

        # upload or copy the targets
        transporter = storage.get_transporter()
        if upload_targets:
            transporter.upload(resources=upload_targets)
        if copy_targets:
            transporter.copy(resources=copy_targets)

        return local_content

    def _not_uploaded(self, targets: [Content], storage: AssetStorage) -> list:
        """Checks if the contents exist either in staging or remote area

        - some objects may have been deleted in previous version and re-added in a later version
        - the content store will already have a copy so those contents need not be re-uploaded

        Parameters
        ----------
        targets: list
            list of Content instances

        Returns
        -------
        list:
            filtered list of Content not present in remote
        """
        # fetch the full list, so we can avoid multiple network calls
        # first check in remote
        remote_contents = set([os.path.basename(blob.name)
                               for blob in storage.list_blobs(url=self.contents.remote_url)])
        committed_contents, local_contents = [], []
        for content in targets:
            # todo: compare hashes also
            if content.file_id in remote_contents:
                content.set_state(content.states.COMMITTED)
                committed_contents.append(content)
            else:
                local_contents.append(content)

        if committed_contents:
            # update the states
            self.contents.update_states(contents=committed_contents, save=True)

        return local_contents
