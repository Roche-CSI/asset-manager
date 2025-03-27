import hmac
import os
from datetime import datetime
from hashlib import sha256

from botocore.auth import S3SigV4Auth

from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_utils.common import exceptions


def get_aws_id_k_date() -> dict:
    """
    TODO: will move it into the server, added for testing purpose only
    Returns
    -------
    str
        the k_date hex string
    """
    secret_key = StorageCredentials.shared().credentials.get("aws_secret_access_key")
    today = datetime.utcnow().strftime('%Y%m%d')  # always use the UTC time for k_date
    hex_k_date = hmac.new(f"AWS4{secret_key}".encode("utf-8"), today.encode("utf-8"), sha256).hexdigest()
    return {"aws_access_key_id": StorageCredentials.shared().credentials.get("aws_access_key_id"),
            "k_date": hex_k_date}


class AwsAuth(S3SigV4Auth):
    """
    Custom AWS authentication class for S3 that uses K_DATE from the environment if the secret key is not provided
    """

    def signature(self, string_to_sign, request):
        """
        Returns the signature for the given string and request

        Parameters
        ----------
        string_to_sign : str
            The string to sign
        request : obj
            The request object

        Returns
        -------
        str
            The signature for the given string and request
        """
        key = self.credentials.secret_key
        if key:
            return super().signature(string_to_sign, request)
        else:
            return self._sign_with_k_date(string_to_sign)

    def _sign_with_k_date(self, string_to_sign):
        """Returns the signature for the given string using K_DATE from the environment

        Parameters
        ----------
        string_to_sign : str
            The string to sign

        Returns
        -------
        str
            The signature for the given string using K_DATE

        Raises
        ------
        AssetException
            If K_DATE is not found in the environment
        """
        k_date_str = os.environ.get("ASSET_K_DATE")
        if not k_date_str:
            raise exceptions.AssetException("ASSET_K_DATE not found in environment")
        k_date = bytes.fromhex(k_date_str)
        k_region = self._sign(k_date, self._region_name)
        k_service = self._sign(k_region, self._service_name)
        k_signing = self._sign(k_service, msg="aws4_request")
        return self._sign(k_signing, string_to_sign, hex=True)
