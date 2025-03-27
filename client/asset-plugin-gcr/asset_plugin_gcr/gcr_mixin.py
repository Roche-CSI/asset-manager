import json

import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from asset_plugin_gcr.gcr_url import GcrURL
from asset_utils.common import exceptions

URL_FORMAT = "https://{host}/v2/{project}/{image}/tags/list"
AUTH_FORMAT = "Bearer {token}"


class GcrMixin:

    def get_gcr_blob(self, url: GcrURL):
        if not url.is_valid():
            raise exceptions.InvalidStorageURLError(f"{exceptions.InvalidStorageURLError.msg}: {url.url}")

        res: dict = self.fetch_url_data(host=url.host,
                                        project=url.project,
                                        image=url.image)
        # we need to parse and filter because it's a list of objects
        return self.parse_url_response(gcr_url=url, url_data=res)

    def fetch_url_data(self, host: str, project: str, image: str) -> dict:
        url = URL_FORMAT.format(host=host, project=project, image=image)
        headers = {"Authorization": AUTH_FORMAT.format(token=self.get_token())}
        res = requests.get(url=url, headers=headers)
        return res.json()

    def parse_url_response(self, gcr_url: GcrURL, url_data: dict):
        image_data = url_data.get("manifest")
        # this is a dict where keys are the hashes
        if not image_data:
            if self.is_permission_error(url_data):
                raise exceptions.InsufficientCredentialError(msg=f"permission denied to: {gcr_url}",
                                                             data=json.dumps(url_data))
            else:
                exceptions.InvalidObjectSourceError(msg=f"not found: {gcr_url}")
        if gcr_url.tag:
            return self._parse_tag_url_response(url=gcr_url, url_data=url_data)
        else:
            return self._parse_sha_url_response(url=gcr_url, url_data=url_data)

    def _parse_tag_url_response(self, url: GcrURL, url_data: dict):
        self._validate_response(data=url_data, url=url)
        image_data = url_data.get("manifest")
        for hash_name in image_data:
            data: dict = image_data.get(hash_name)
            if data and url.tag in data.get("tag"):
                data['hash_type'], data['hash_value'] = hash_name.split(":")
                data['name'] = url_data.get("name")
                return data

    def _parse_sha_url_response(self, url: GcrURL, url_data: dict):
        self._validate_response(data=url_data, url=url)
        image_data = url_data.get("manifest")
        for hash_name in image_data:
            if hash_name == url.hash:
                found = image_data.get(hash_name)
                found['hash_type'], found['hash_value'] = hash_name.split(":")
                found['name'] = url_data.get("name")
                return found

    def _validate_response(self, data: dict, url: GcrURL):
        # this is a dict where keys are the hashes
        if not data.get("manifest"):
            if self.is_permission_error(data):
                raise exceptions.InsufficientCredentialError(
                    msg=f"{exceptions.InsufficientCredentialError.msg}, permission denied to:{url}")
            else:
                exceptions.InvalidObjectSourceError(msg=f"f{url.url} not found")

    def is_permission_error(self, url_data: dict) -> bool:
        errors = url_data.get("errors", [])
        for error in errors:
            if error.get("code") == "DENIED":
                return True
        return False

    def get_token(self) -> str:
        """
        https://stackoverflow.com/questions/53472429/how-to-get-a-gcp-bearer-token-programmatically-with-python

        Returns
        -------
        str:
            token
        """
        # TODO: return the token from the credentials after auth refactor
        credentials = Credentials.from_service_account_info(self.credentials,
                                                            scopes=['https://www.googleapis.com/auth/cloud-platform'])

        credentials.refresh(Request())
        return credentials.token
