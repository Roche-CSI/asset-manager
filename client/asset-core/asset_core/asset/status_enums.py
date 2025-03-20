from asset_core.configs import AppSettings
from asset_utils.common import exceptions


class StatusEnums:
    """Enum for asset status.

    Status can only be updated through asset-dashboard.
    """
    PUBLIC = 1  # default, anyone can download/upload
    PRIVATE = 2  # only Asset-Owner or Project-Admin can download/upload
    DELETED = 3  # flagged for deletion, no one can download/upload
    DEPRECATED = 4  # everyone can download (warn user), no one can upload
    OBSOLETE = 5  # Project-Admin can download, no one can upload
    ARCHIVE_FLAGGED = 6  # flagged for archiving, permissions same as ARCHIVED
    ARCHIVED = 7  # everyone can download (special permission), no one can upload (frozen permanently)

    @classmethod
    def from_string(cls, value):
        """
        Convert a string to its corresponding numeric value.
        Accepts both the string representation of the number or the status name.
        """
        try:
            # Try to convert to int directly
            return int(value)
        except ValueError:
            # If not a number, try to match the name
            status_name = value.upper()
            for name, num_value in cls.__dict__.items():
                if name.isupper() and name == status_name:
                    return num_value
            raise exceptions.AssetException(f"'{value}' is not a valid status")

    @classmethod
    def to_string(cls, value):
        """
        Convert a numeric value to its corresponding string.
        """
        for name, num_value in cls.__dict__.items():
            if name.isupper() and num_value == value:
                return name
        raise exceptions.AssetException(f"'{value}' is not a valid status")

    @classmethod
    def default(cls):
        return cls.PUBLIC

    @classmethod
    def can_upload(cls, asset) -> bool:
        # check the status of the asset-class first
        if asset.asset_class.status > cls.PRIVATE:
            raise exceptions.AssetException(f"asset class: {asset.asset_class.name} can not be uploaded: "
                                            f"{cls.to_string(asset.asset_class.status)}")
        if asset.asset_class.status == cls.PRIVATE:
            if not cls.is_project_admin() and not cls.is_owner(asset.asset_class.owner):
                e = exceptions.AssetException(f"asset class: {asset.asset_class.name} can not be uploaded: "
                                              f"{cls.to_string(asset.asset_class.status)}")
                e.logs.add("only project admin or class owner can upload to this asset class")
                raise e

        # check the status of the asset
        if asset.status > cls.PRIVATE:
            raise exceptions.AssetException(f"asset: {asset.name} can not be uploaded: {cls.to_string(asset.status)}")
        if asset.status == cls.PRIVATE:
            if not cls.is_project_admin() and not cls.is_owner(asset.owner):
                e = exceptions.AssetException(f"asset: {asset.name} can not be uploaded: {cls.to_string(asset.status)}")
                e.logs.add("only project admin or asset owner can upload to this asset")
                raise e
        return True

    @staticmethod
    def is_project_admin() -> bool:
        """Check if the user is a project admin."""
        active_data = AppSettings.shared().active_project_data
        return active_data.get("can_admin_project", False)

    @staticmethod
    def is_owner(owner) -> bool:
        """Check if the user is the asset owner."""
        return owner == AppSettings.shared().user.get("username")

    @classmethod
    def can_download(cls, status, owner) -> bool:
        if status == cls.PRIVATE:
            if cls.is_project_admin() or cls.is_owner(owner):
                return True
            return False
        elif status == cls.DELETED:
            return False
        elif status == cls.OBSOLETE:
            if cls.is_project_admin():
                return True
            return False

        return True
