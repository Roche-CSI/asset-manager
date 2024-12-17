from asset_core.asset.asset_diff import AssetDiff
from asset_utils.utils.log_utils import LogColors, colored_string
from .repo import RepoAPI


class VersionAPI(RepoAPI):
    """A class used to manage versions of an asset."""

    def list_versions_summary(self, jsonize=False):
        """Lists versions summary of an asset.

        Parameters
        ----------
        jsonize : bool, optional
            Whether to return the data in JSON format, by default False.

        Returns
        -------
        dict or None
            The versions data if jsonize is True, otherwise None.
        """
        if self.asset.is_temp:
            # local asset
            message = colored_string(f"asset: {self.asset.name}\n", LogColors.INFO)
            message += colored_string("versions not available\n", LogColors.ERROR)
            message += "this is a local asset and has not been uploaded and versioned"
            self.user_log.message(message)
            return None
        versions = self.asset.cached_versions()
        if jsonize:
            keys = ["created_by", "created_at", "commit_hash", "commit_message", "size"]
            data = {}
            for version in versions:
                summary = {key: version[key] for key in keys if version.get(key)}
                data[version["number"]] = summary
            return data

        # print to terminal otherwise
        self.user_log.message(f"asset: {self.asset.name}", LogColors.INFO)
        self.versions_summary_table(versions=versions)

    def versions_summary_table(self, versions: [dict]):
        """Prints a summary table of versions.

        Parameters
        ----------
        versions : list
            The list of versions.
        """
        columns = {
            "version": "Version",
            "commit_hash": "Commit",
            "size": "Size",
        }
        rows = [
            {
                'version': self.active_version_color(
                    version_number=version.get('number'),
                    data=version.get('number')
                ),
                'commit_hash': self.active_version_color(
                    version_number=version.get('number'),
                    data=version.get('commit_hash')
                ),
                'size': self.active_version_color(
                    version_number=version.get('number'),
                    data=version.get('size')
                ),
            } for version in versions]
        self.user_log.table(columns=columns, rows=rows, table_fmt="simple")

    def active_version_color(self, version_number: str, data: str, active_version=None) -> str:
        """Returns the data in color if the version number is the active version.

        Parameters
        ----------
        version_number : str
            The version number.
        data : str
            The data to be colored.
        active_version : str, optional
            The active version number, by default None.

        Returns
        -------
        str
            The colored data if the version number is the active version, otherwise the original data.
        """
        if not active_version:
            active_version = self.active_version()
        if active_version == version_number:
            return colored_string(data, LogColors.ACTIVE)
        return data

    def active_version(self) -> str:
        """Returns the active version number of the asset.

        Returns
        -------
        str
            The active version number.
        """
        return self.asset.version.number

    def name(self) -> str:
        """Returns the name of the asset.

        Returns
        -------
        str
            The name of the asset.
        """
        return self.asset.version.name

    def list_version_history(self, large=False, jsonize=False):
        """Lists history of all versions of an asset.

        Parameters
        ----------
        large : bool, optional
            Whether to display a large table, by default False.
        jsonize : bool, optional
            Whether to return the data in JSON format, by default False.

        Returns
        -------
        dict or None
            The versions data if jsonize is True, otherwise None.
        """
        if self.asset.is_temp:
            # local asset
            message = colored_string(f"asset: {self.asset.name}\n", LogColors.INFO)
            message += colored_string("history not available\n", LogColors.ERROR)
            message += "this is a local asset and has not been uploaded and versioned"
            self.user_log.message(message)
            return None
        versions = self.asset.cached_versions()
        if jsonize:
            keys = ["created_by", "created_at", "commit_hash", "commit_message", "patch"]
            history_data = {}
            asset_diff = AssetDiff()
            for version in versions:
                summary = {key: version[key] for key in keys}
                # remove the patch from json and replace with user-friendly data
                added, removed, altered = asset_diff.file_changed(patch=summary.pop("patch"))
                summary["added"] = added or "None"
                summary["removed"] = removed or "None"
                summary["altered"] = altered or "None"
                # add the summary to the history data
                history_data[version["number"]] = summary
            return history_data

        self.user_log.message(f"asset: {self.asset.name}", LogColors.INFO)
        self.version_history_table(versions=versions, large=large)

    def version_history_table(self, versions: [dict], large=False):
        """Prints a table of version history.

        Parameters
        ----------
        versions : list
            The list of versions.
        large : bool, optional
            Whether to display a large table, by default False.
        """
        if large:
            columns = {
                "number": "Version",
                "created_at": "Created At",
                "added": "Files Added",
                "removed": "Files Removed",
                "altered": "Files Altered",
                "created_by": "Created By",
                "commit_hash": "Commit Hash",
                "commit_message": "Commit Message",
            }
        else:
            columns = {
                "number": "Version",
                "added": "Files Added",
                "removed": "Files Removed",
                "altered": "Files Altered",
            }

        data = [self.version_history_row(columns=columns, version_data=version) for version in versions]
        self.user_log.table(columns=columns, rows=data, table_fmt="grid")

    def version_history_row(self, columns: dict, version_data: dict) -> dict:
        """Returns a row of the version history table.

        Parameters
        ----------
        columns : dict
            The columns of the table.
        version_data : dict
            The version data.

        Returns
        -------
        dict
            The row of version data.
        """
        asset_diff = AssetDiff()
        added, removed, altered = asset_diff.file_changed(patch=version_data.get("patch"))
        version_data["added"] = "\n".join(added) if added else "None"
        version_data["removed"] = "\n".join(removed) if removed else "None"
        version_data["altered"] = "\n".join(altered) if altered else "None"

        return {column: version_data.get(column) for column in columns}
