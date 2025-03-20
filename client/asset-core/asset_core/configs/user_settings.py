import os

from asset_core.configs.settings_prop import SettingsProp
from asset_utils.common import exceptions
from asset_utils.utils import update_dict

INACTIVE_KEYS = ["asset_credentials"]


class UserSettings:

    def __init__(self, app_settings=None):
        self.pre_init()
        if app_settings:
            self.app_settings = app_settings
            self.update(app_settings.data.get('user_configs') or {})

    @classmethod
    def default(cls):
        return UserSettings()

    def pre_init(self):
        self.upload_timeout = SettingsProp(value=3600,
                                           data_type=int,
                                           unit="seconds per file",
                                           name="ASSET_UPLOAD_TIMEOUT",
                                           help="timeout per file, for uploading files to remote storage")
        self.download_timeout = SettingsProp(value=3600,
                                             data_type=int,
                                             unit="seconds per file",
                                             name="ASSET_DOWNLOAD_TIMEOUT",
                                             help="timeout per file, for downloading files from remote storage")
        self.num_retries = SettingsProp(value=5,
                                        data_type=int,
                                        unit="number of retries",
                                        name="ASSET_DOWNLOAD_RETRIES",
                                        help="number of retry attempts for downloading files from remote storage")
        self.dont_ask_user = SettingsProp(value=False,
                                          data_type=bool,
                                          unit="true/false",
                                          name="ASSET_DONT_ASK_USER",
                                          help="don't ask user for confirmation")
        self.linking_type = SettingsProp(value="copy",
                                         data_type=str,
                                         unit="copy | hardlink | symlink",
                                         name="ASSET_OBJECT_LINKING",
                                         help="linking type for files, defaults to copy")
        self.batch_size = SettingsProp(value=16,
                                       data_type=int,
                                       unit="number of requests",
                                       name="ASSET_BATCH_SIZE",
                                       help="max number of concurrent requests for upload/download/copy operations")
        self.bucket_mt_config = SettingsProp(value={},
                                             data_type=dict,
                                             unit="dictionary",
                                             name="ASSET_BUCKET_MT_CONFIG",
                                             help='mounting configurations for buckets, e.g "bucket_url:mount_path"')
        self.server_url = SettingsProp(value=None,
                                       data_type=str,
                                       unit="url string",
                                       name="ASSET_SERVER_URL",
                                       help="asset-manager server url")
        self.server_access = SettingsProp(value=False,
                                          data_type=bool,
                                          unit="true/false",
                                          name="ASSET_SERVER_ACCESS",
                                          help="if client has access to asset-manager server")
        self.dashboard_url = SettingsProp(value=None,
                                          data_type=str,
                                          unit="url string",
                                          name="ASSET_DASHBOARD_URL",
                                          help="asset-manager dashboard url")

    def update(self, kwargs):
        for key in kwargs:
            if key in INACTIVE_KEYS:
                continue
            if hasattr(self, key):
                attr = getattr(self, key)
                if isinstance(attr, SettingsProp):
                    attr.value = attr.validate(kwargs.get(key))  # will raise exception if invalid
                else:
                    raise exceptions.AssetException("Invalid config_key: {}".format(key))
            else:
                raise exceptions.AssetException("Invalid config_key: {}".format(key))

    def reset(self, key: str):
        if hasattr(self, key):
            attr = getattr(self, key)
            if isinstance(attr, SettingsProp):
                setattr(self, key, getattr(UserSettings.default(), key))
            else:
                raise exceptions.AssetException("Invalid config_key: {}".format(key))
        else:
            raise exceptions.AssetException("Invalid config_key: {}".format(key))

    def validate(self):
        for key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, SettingsProp):
                if attr.unit is None:
                    # null value is permitted
                    raise ValueError("Missing unit for {}".format(key))
                if attr.name is None:
                    raise ValueError("Missing environment variable name for {}".format(key))

    def activate(self):
        for key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, SettingsProp):
                # allow for user to override using the environment variable directly
                if attr.value is not None and attr.name not in os.environ:
                    os.environ[attr.name] = SettingsProp.to_string(attr.value) if not isinstance(attr.value,
                                                                                                 str) else attr.value

    def deactivate(self):
        for key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, SettingsProp):
                if attr.name in os.environ:
                    # check if it's the same as the current value, if not, then user has set it - so we ignore
                    if SettingsProp.to_string(attr.value) == os.environ[attr.name]:
                        del os.environ[attr.name]

    def serialize(self):
        data = {}
        for key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, SettingsProp):
                data[key] = attr.value
        return data

    def printable_format(self):
        default_stg = UserSettings.default().serialize()
        data = {}
        for key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, SettingsProp):
                data[key] = {
                    "value": SettingsProp.to_string(attr.value),
                    "type": attr.unit,
                    "default": SettingsProp.to_string(default_stg.get(key)),
                }
        return data

    def save(self):
        self.app_settings.data = update_dict(self.app_settings.data, {'user_configs': self.serialize()})
