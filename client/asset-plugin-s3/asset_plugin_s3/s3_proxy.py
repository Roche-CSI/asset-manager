import io
import os
from typing import Optional, Dict, Any, List

import requests


class S3Proxy:
    """
    Class to act as proxy for fetching data from S3 bucket.
    This will connect to the asset-backend to collect the necessary data.
    We use this in case of mounted bucket to fetch data from S3 bucket.
    """

    def __init__(self, asset_backend_url: str):
        self.asset_backend_url = asset_backend_url
        self.route = "bucket_proxy"

    def _make_request(self, endpoint: str, method: str = 'GET',
                      data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a request to the asset-backend."""
        url = os.path.join(self.asset_backend_url, self.route, endpoint)
        response = requests.request(method, url, json=data)
        response.raise_for_status()
        return response

    def get_object(self, url: str) -> dict:
        """Get an object from the bucket."""
        response = self._make_request(endpoint="get_object",
                                      method="POST",
                                      data={"blob_url": url})
        return response.json()

    def list_objects(self, url: str) -> List[Dict[str, Any]]:
        """Get a list of objects from the bucket."""
        response = self._make_request(endpoint="list_objects",
                                      method="POST",
                                      data={"blob_url": url})
        return response.json()

    def put_object(self, key: str, data: io.BytesIO) -> Dict[str, Any]:
        raise NotImplementedError

    def delete_object(self, key: str) -> Dict[str, Any]:
        """Delete an object from the bucket."""
        raise NotImplementedError

    def get_object_metadata(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Get metadata of an object in the bucket."""
        raise NotImplementedError

    def copy_object(self, source_key: str, dest_key: str) -> Dict[str, Any]:
        """Copy an object within the same bucket."""
        raise NotImplementedError

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for an object."""
        raise NotImplementedError
