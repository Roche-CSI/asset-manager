import json
import warnings
from urllib import parse

import requests

from asset_utils.common import exceptions


class BaseServer:
    configs = None

    @property
    def url(self):
        return self.configs.server_url

    def parse(self, res):
        return json.loads(res.content)

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
                response = requests.get(url=url, verify=self.configs.ssl_verify)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                raise exceptions.IncorrectServerResponseError(msg=f"invalid server response: {e}")
            except Exception as e:
                raise exceptions.ServerNotAvailableError(msg=f"unable to reach asset-server: {e}")

    def put(self, url: str, data: dict):
        with warnings.catch_warnings(record=True) as _:
            try:
                response = requests.put(url=url, data=json.dumps(data), verify=self.configs.ssl_verify)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                raise exceptions.IncorrectServerResponseError(msg=f"invalid server response: {e}")
            except Exception as e:
                raise exceptions.ServerNotAvailableError(msg=f"unable to reach asset-server: {e}")

    def post(self, url: str, data: dict):
        with warnings.catch_warnings(record=True) as _:
            try:
                response = requests.post(url=url, data=json.dumps(data), verify=self.configs.ssl_verify)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                raise exceptions.IncorrectServerResponseError(msg=f"invalid server response: {e}")
            except Exception as e:
                raise exceptions.ServerNotAvailableError(msg=f"unable to reach asset-server: {e}")
