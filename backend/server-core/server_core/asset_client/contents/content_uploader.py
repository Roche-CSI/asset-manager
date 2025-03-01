from server_core.asset_client.contents.content import Content
from server_core.gcp import list_url_blobs
from server_core.utils.logging import LoggingMixin
from gcloud.aio.storage import Storage as aioStorage
from .content_set import ContentSet
import asyncio
import aiohttp
import os


class ContentUploader(LoggingMixin):
    contents: ContentSet = None

    def __init__(self, contents):
        self.contents = contents

    def commit_contents(self):
        """Uploads to staging
        - filter out contents that exist either in staging area or in remote area
        - upload the remaining objects into staging area
        """
        # get targets
        to_commit = self._not_committed(targets=list(self.contents.filter(lambda x: x.can_commit)))
        if not to_commit:
            return []

        # 2 change state
        for content in to_commit:
            content.state = Content.states.COMMITTING

        # 3 upload to remote
        self._upload(to_commit)

        # check all contents got committed
        # to ensure atomicity - we reject the transaction even if there is one failure
        for content in to_commit:
            if content.state != Content.states.COMMITTED:
                raise Exception(f"failed to commit content:{content.serialize()}")

    def _upload(self, contents):
        return asyncio.run(self._upload_to_remote(contents=contents))

    async def _upload_to_remote(self, contents: list):
        # disable ssl verification, throws errors on some Macs otherwise
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async_client = aioStorage(session=session)
            await asyncio.gather(*[
                content.transfer_to_remote(aio_client=async_client) for content in contents
            ])
            self.log.info("completed upload")

    def _not_committed(self, targets: [Content]) -> list:
        """ Checks if the contents exist either in staging or remote area
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
        # fetch the full list so we can avoid multiple network calls
        remote_contents = set([os.path.basename(blob.name) for blob in list_url_blobs(self.contents.remote_url)])
        committed, staged = [], []
        for content in targets:
            if content.file_id in remote_contents:
                content.state = content.states.COMMITTED
                committed.append(content)
            else:
                content.state = content.states.STAGED
                staged.append(content)

        return staged

