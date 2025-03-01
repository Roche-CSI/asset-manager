import contextlib
import json

from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_pluggy.storage.storage_factory import StorageFactory
from cryptography.fernet import Fernet
from peewee import *
from playhouse.postgres_ext import JSONField

from server_core.models.app_secret import AppSecret
from server_core.models.base.read_write import ReadWriteModel


class Bucket(ReadWriteModel):
    title = CharField(null=True)
    bucket_url = CharField(unique=True)
    keys = TextField(null=True)
    description = TextField(null=True)
    is_active = BooleanField(null=False, default=True)
    configs = JSONField(null=True, default=dict)

    @staticmethod
    def fernet():
        key_name = "fernet"
        secret = AppSecret.get_or_none(AppSecret.name == key_name)
        if not secret:
            new_key = Fernet.generate_key().decode()
            secret = AppSecret.create(user="system", name=key_name, secret=new_key)
        return Fernet(secret.secret.encode())

    @classmethod
    def encrypt_keys(cls, keys):
        fernet = cls.fernet()
        if isinstance(keys, dict):
            keys_str = json.dumps(keys)
        elif isinstance(keys, str):
            keys_str = keys
        else:
            raise ValueError("Keys must be either a string or a dictionary")
        return fernet.encrypt(keys_str.encode()).decode()

    @classmethod
    def decrypt_keys(cls, encrypted_keys):
        fernet = cls.fernet()
        decrypted = fernet.decrypt(encrypted_keys.encode()).decode()
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted

    def save(self, user=None, force_insert=False, only=None):
        self.bucket_url = self.bucket_url.lower()
        self.keys = self.__class__.encrypt_keys(self.keys)
        return super().save(user=user, force_insert=force_insert, only=only)

    def _decrypt_keys(self):
        try:
            return self.__class__.decrypt_keys(self.keys)
        except Exception as e:
            print(f"Error decrypting keys for bucket {self.bucket_url}: {str(e)}")
            return None

    @contextlib.contextmanager
    def permissions(self):
        # set credentials
        StorageCredentials.shared().set_credentials(self.decrypt_keys(self.keys))
        yield
        # clear credentials
        StorageCredentials.shared().set_credentials(None)

    @property
    def storage(self):
        return StorageFactory.storage_for_url(self.bucket_url)

    @staticmethod
    def get_bucket_url(blob_url):
        """
        Extract the bucket URL from a given GS or S3 blob URL.

        Args:
        blob_url (str): The full blob URL (e.g., 's3://bucket/path/to/file' or 'gs://bucket/path/to/file')

        Returns:
        str: The bucket URL (e.g., 's3://bucket' or 'gs://bucket')

        Raises:
        ValueError: If the URL doesn't start with 's3://' or 'gs://'
        """
        # List of supported protocols
        protocols = ['s3://', 'gs://']

        # Check if the URL starts with a supported protocol
        protocol = next((p for p in protocols if blob_url.startswith(p)), None)

        if not protocol:
            raise ValueError(f"URL must start with one of {', '.join(protocols)}")

        # Remove the protocol and split the remaining string
        parts = blob_url[len(protocol):].split('/', 1)

        # The bucket name is the first part after removing the protocol
        bucket = parts[0]

        return f'{protocol}{bucket}'
