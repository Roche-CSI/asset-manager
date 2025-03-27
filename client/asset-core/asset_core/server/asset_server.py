import json
import os
import warnings
from urllib import parse

import requests

from asset_core.configs import Configs, AppSettings
from asset_utils.common import exceptions
from asset_utils.utils import UserLog


class AssetServer:
    configs = None

    def __init__(self):
        self.configs = Configs.shared().server

    @property
    def url(self):
        return self.configs.server_url

    @property
    def headers(self):
        bearer_token = AppSettings.shared().user.get('token')
        return {
            "Authorization": f"Bearer {bearer_token}",
        }

    def _asset_route(self, id=None):
        base = os.path.join(self.url, self.configs.asset_route)
        return os.path.join(base, id) if id else base

    def _asset_class_route(self, id=None):
        base = os.path.join(self.url, self.configs.asset_class_route)
        if not base.endswith("/"):
            base += "/"
        return os.path.join(base, id) if id else f"{base}"

    def _asset_commit_route(self, id=None):
        base = os.path.join(self.url, self.configs.asset_commit_route)
        return os.path.join(base, id) if id else base

    def _asset_version_route(self, id=None):
        base = os.path.join(self.url, self.configs.asset_version_route)
        return os.path.join(base, id) if id else base

    def _find_version_route(self):
        return os.path.join(self.url, self.configs.find_version_route)

    def _asset_ref_route(self):
        return os.path.join(self.url, self.configs.asset_ref_route)

    def _find_ref_route(self):
        return os.path.join(self.url, self.configs.find_ref_route)

    def create_asset(self, **kwargs):
        return self.parse(self.post(url=self._asset_route(), data=kwargs))

    def find_asset(self, **kwargs):
        url = self.add_params(self._asset_route(), {**kwargs, "name": True})
        return self.parse(self.get(url=url))

    def create_asset_class(self, **kwargs) -> dict:
        return self.parse(self.post(url=self._asset_class_route(), data=kwargs))

    def update_asset(self, id, data: dict):
        return self.parse(self.put(url=self._asset_route(id), data=data))

    def update_refs(self, data: dict):
        return self.parse(self.post(url=self._asset_ref_route(), data=data))

    def find_refs(self, asset_name: str, project_id: str):
        url = self.add_params(url=self._asset_ref_route(),
                              params={"asset_name": asset_name,
                                      "project_id": project_id})
        return self.parse(self.get(url=url))

    def commit_asset(self, id, data: dict, message=None):
        res = self.put(url=self._asset_commit_route(id),
                       data={"payload": data,
                             "message": message})
        return self.parse(res=res), res.status_code

    def get_asset_yaml(self, id):
        return self.parse(self.get(url=self._asset_commit_route(id)))

    def get_asset(self, id):
        return self.parse(self.get(url=self._asset_route(id)))

    def find_asset_versions(self, project_id: str,
                            version_names: list = None,
                            class_name: str = None,
                            commit_hash: str = None):
        if not project_id:
            raise exceptions.NoActiveProjectError()

        data = {'project_id': project_id}
        if version_names:
            data['version_names'] = version_names
        if class_name:
            data['class_name'] = class_name
        if commit_hash:
            data['commit_hash'] = commit_hash
            data['name'] = True
        if not version_names and not commit_hash:
            raise exceptions.InvalidArgumentError("missing required parameter: hash")

        url = self.add_params(self._asset_version_route(), data)
        return self.parse(self.get(url=url))

    def get_version(self, project_id, class_id, seq_id, version_number=None):
        """Retrieves the specific version object from the server."""
        url = self.add_params(url=self._asset_version_route(),
                              params={"project_id": project_id,
                                      "class_id": class_id,
                                      "seq_id": seq_id,
                                      "version_number": version_number,
                                      "leaf_version": not version_number})
        data = self.parse(self.get(url=url))
        # server might return a list since it's hitting a common end point
        return data[0] if isinstance(data, list) else data

    def update_asset_class(self, id, data: dict):
        self.parse(self.put(url=self._asset_class_route(id), data=data))

    def parse(self, res):
        try:
            return json.loads(res.content)
        except json.decoder.JSONDecodeError as e:
            raise exceptions.IncorrectServerResponseError(
                msg=f"unable to parse server response: {res.content}") from e

    def add_params(self, url, params: dict):
        """adds query params to url"""
        parsed = parse.urlparse(url)
        query = parsed.query
        url_dict = dict(parse.parse_qsl(query))
        url_dict.update(params)
        url_new_query = parse.urlencode(url_dict, True)
        parsed = parsed._replace(query=url_new_query)
        return parse.urlunparse(parsed)

    def get(self, url: str):
        with warnings.catch_warnings(record=True) as _:
            try:
                response = requests.get(url=url,
                                        headers=self.headers,
                                        verify=self.configs.ssl_verify)
                response.raise_for_status()
                self.check_asset_warnings(response)
                return response
            except requests.exceptions.HTTPError as e:
                raise exceptions.IncorrectServerResponseError(msg=f"invalid server response: {e}")
            except Exception as e:
                raise exceptions.ServerNotAvailableError(msg=f"unable to reach asset-server: {e}")

    def put(self, url: str, data: dict):
        with warnings.catch_warnings(record=True) as _:
            try:
                response = requests.put(url=url,
                                        data=json.dumps(data),
                                        headers=self.headers,
                                        verify=self.configs.ssl_verify)
                response.raise_for_status()
                self.check_asset_warnings(response)
                return response
            except requests.exceptions.HTTPError as e:
                raise exceptions.IncorrectServerResponseError(msg=f"invalid server response: {e}")
            except Exception as e:
                raise exceptions.ServerNotAvailableError(msg=f"unable to reach asset-server: {e}")

    def post(self, url: str, data: dict):
        with warnings.catch_warnings(record=True) as _:
            try:
                response = requests.post(url=url,
                                         data=json.dumps(data),
                                         headers=self.headers,
                                         verify=self.configs.ssl_verify)
                response.raise_for_status()
                self.check_asset_warnings(response)
                return response
            except requests.exceptions.HTTPError as e:
                raise exceptions.IncorrectServerResponseError(msg=f"invalid server response: {e}")
            except Exception as e:
                raise exceptions.ServerNotAvailableError(msg=f"unable to reach asset-server: {e}")

    def check_asset_warnings(self, response):
        """Check for warnings in the response and print them.

        If the status code is less than 200, we have a warning.
        The warning message is in the response header.
        """
        if response.status_code < 200:
            # print the warning message is in the response header
            UserLog().alert(response.headers.get('Warning', 'Missing warning message from server'))
