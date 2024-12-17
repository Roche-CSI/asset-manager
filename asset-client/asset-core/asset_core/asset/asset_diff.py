import os

from asset_core.asset import Asset
from asset_core.asset.asset_ignore import AssetIgnore
from asset_core.objects import Object
from asset_core.plugins import exceptions, FileUtils
from asset_core.store import Repo
from asset_db.db import Database
from asset_utils.utils import files_at_location, relative_path


class AssetDiff:
    """A class used to compute the differences between two versions of an asset."""

    def create_asset_manifest(self,
                              asset: Asset = None,
                              repo: Repo = None,
                              asset_name: str = None,
                              ver_number: str = None,
                              force: bool = False) -> str:
        """Creates the asset manifest file by combining asset.yaml, version_<>.yaml, and objects.yaml.

        Parameters
        ----------
        asset : Asset, optional
            The asset object, by default None.
        repo : Repo, optional
            The repo object, by default None.
        asset_name : str, optional
            The name of the asset, by default None.
        ver_number : str, optional
            The version number of the asset, by default None.
        force : bool, optional
            If False, we don't create if the file exists, by default False.

        Returns
        -------
        str
            The path to the manifest file.
        """
        asset = asset or Asset.retrieve(repo=repo, asset_name=asset_name)

        if not ver_number or ver_number != asset.version.number:
            version = self.check_version(asset.cached_versions(), ver_number=ver_number)
            if version:
                asset.version.de_serialize(asset=asset, data=version)

        manifest_file = asset.manifest_file
        if manifest_file and os.path.exists(manifest_file):
            return manifest_file

        cached_file = self.create_cached_manifest_file(asset=asset, force=force)
        FileUtils.copy_file(src=cached_file, dst=manifest_file)
        return manifest_file

    def create_cached_manifest_file(self, asset: Asset, force: bool = False) -> str:
        """Creates the cached asset manifest file.

        Parameters
        ----------
        asset : Asset
            The asset object.
        force : bool, optional
            If False, we don't create if the file exists, by default False.

        Raises
        ------
        Exception
            If the asset is temporary or the version number is invalid.

        Returns
        -------
        str
            The path to the cached manifest file.
        """
        if asset.is_temp:
            # no cached data for temp asset
            raise exceptions.AssetException("temporary asset, can not create manifest")

        if not asset.version or not asset.version.number:
            raise exceptions.InvalidVersionError("invalid asset version")

        # check if file exists in cache
        cached_file = asset.repo.store.cached_manifest_file(asset_id=asset.id, ver_number=asset.version.number)
        if not os.path.exists(cached_file) or force:
            asset_data = self.manifest_data(asset=asset, version=asset.version.serialize())
            if not asset_data:
                raise exceptions.AssetNotFoundError("asset not found locally")

            Database.write(data=asset_data, path=cached_file)
        return cached_file

    def manifest_data(self, asset: Asset, version: dict = None, ver_number: str = None) -> dict:
        """Creates the asset manifest data for a specific version of the asset.

        Take all version whose ids are less than the given version id and combine those

        Parameters
        ----------
        asset : Asset
            The asset object.
        version : dict, optional
            The version data, by default None.
        ver_number : str, optional
            The version number, by default None.

        Returns
        -------
        dict
            The asset manifest data.
        """
        asset_data = asset.serialize()
        if asset.is_temp:
            return asset_data

        versions: [dict] = asset.cached_versions()  # this is a sorted list by ids
        target_version = version or self.check_version(versions=versions, ver_number=ver_number)
        object_ids = self.resolve_versions(versions, upto_version=target_version)
        # try in v2 directory first
        objects: dict = asset.cached_objects_v2()
        if not objects:
            # if not v2 then try in v1
            objects = asset.cached_objects()
        version_objects = []
        for id, object in objects.items():
            if id in object_ids:
                version_objects.append(object)
                # pop the id, so we can do error check in the end
                object_ids.discard(id)

        if len(object_ids) > 0:
            raise Exception(f"missing objects:{','.join(object_ids)}")

        asset_data["version"] = target_version
        asset_data["objects"] = version_objects
        return asset_data

    def check_version(self, versions: [dict], ver_number: str) -> dict:
        """Checks the version of the asset.

        Parameters
        ----------
        versions : list
            The list of versions.
        ver_number : str
            The version number.

        Raises
        ------
        InvalidVersionError
            If the version number is invalid.

        Returns
        -------
        dict
            The version data.
        """
        if versions and not ver_number:
            # sort by version number from earliest to latest
            versions.sort(key=lambda v: list(map(int, v["number"].split('.'))))
            # return the latest
            return versions[len(versions) - 1]

        for version in versions:
            if version.get("number") == ver_number:
                return version

        raise exceptions.InvalidVersionError(f"version:{ver_number} is invalid")

    def resolve_versions(self, versions: [dict], upto_version: dict) -> set:
        """Resolves versions to arrive at a final list of objects.

        Parameters
        ----------
        versions : list
            The list of versions.
        upto_version : dict
            The target version.

        Returns
        -------
        set
            The final list of objects.
        """
        result = set()
        for version in versions:
            if version.get("id") <= upto_version.get("id"):
                result = self.apply_patch(base=result, patch=version.get("patch"))
        return result

    def apply_patch(self, base: set, patch: dict) -> set:
        """Applies the patch to the base set of objects.

        Parameters
        ----------
        base : set
            The base set of objects.
        patch : dict
            The patch data.

        Returns
        -------
        set
            The updated set of objects.
        """
        added = patch["added"]
        removed = patch["removed"]
        # add and remove changes
        for item in added:
            base.add(item)

        for item in removed:
            base.discard(item)
        return base

    def compute_diff(self, from_objects=None, to_objects=None) -> dict:
        """Computes the differences between two objects lists.

        Objects are immutable, so the differences are explained
        in terms of objects added and objects removed. Also note that the diff data only contains the object_ids
        i.e. the pointers to the actual objects. This optimizes storage, downloads and the added benefits:
          - allows us the flexibility of schema modifications in future
          - implement the feature branching and merge should we decide to do so

        Parameters
        ----------
        from_objects : list, optional
            The list of objects from which the differences are computed, by default None.
        to_objects : list, optional
            The list of objects to which the differences are computed, by default None.

        Returns
        -------
        dict
            The difference data.
        """
        from_objects = from_objects or set()
        to_objects = to_objects or set()

        # allow for lists also
        if type(from_objects) is list:
            from_objects = set(from_objects)

        if type(to_objects) is list:
            to_objects = set(to_objects)

        removed = []
        added = []
        for item in from_objects:
            if item not in to_objects:
                removed.append(item)

        for item in to_objects:
            if item not in from_objects:
                added.append(item)

        return {
            "added": added,
            "removed": removed
        }

    def file_changed(self, patch: dict) -> tuple:
        """Checks if a file has been changed.

        Parameters
        ----------
        patch : dict
            The patch data.

        Returns
        -------
        list
            The lists of added, removed, and altered files.
        """
        if not patch:
            return [], [], []

        added = {Object.parse_id(id=id)[1] for id in patch.get("added", [])}
        removed = {Object.parse_id(id=id)[1] for id in patch.get("removed", [])}

        # if it appears in the both, then user changed the file content
        # we show it as altered
        altered = {path for path in added if path in removed}
        # pop from added and removed
        for path in altered:
            added.discard(path)
            removed.discard(path)

        return added, removed, altered

    def staged_changes(self, asset: Asset) -> dict or None:
        """Logs out the tracked changes to an asset.

        Additions and removals done by the user.

        Parameters
        ----------
        asset : Asset
            The asset object.

        Returns
        -------
        dict or None
            The tracked changes data if there are any changes, otherwise None.
        """
        # no changes updated if state is not pending
        if not asset.get_state() == asset.states.PENDING:
            return None
        if not asset.is_temp:
            # local asset only so no tracked changes
            cached_manifest = asset.cached_manifest_data()
            cached_objects = cached_manifest.get("objects", [])
        else:
            cached_objects = []

        from_objects = [object.get("id") for object in cached_objects]
        to_objects = [object.id for object in asset.objects]
        added, removed, altered = self.file_changed(patch=self.compute_diff(from_objects, to_objects))
        if added or removed or altered:
            return {
                "added": added,
                "removed": removed,
                "altered": altered
            }
        return None

    def unstaged_changes(self, asset: Asset) -> dict or None:
        """Returns the untracked changes to an asset.

        Parameters
        ----------
        asset : Asset
            The asset object.

        Returns
        -------
        dict or None
            The untracked changes data if there are any changes, otherwise None.
        """
        deleted = []
        modified = []
        unchanged = []
        for obj in asset.objects:
            edit_status = obj.edit_status()
            if edit_status == obj.edit_statuses.DELETED:
                deleted.append(obj)
            elif edit_status == obj.edit_statuses.MODIFIED:
                modified.append(obj)
            else:
                unchanged.append(obj)
        if deleted or modified:
            return {
                "deleted": deleted,
                "modified": modified
            }
        return None

    def untracked_changes(self, asset: Asset) -> dict or None:
        """Returns the list of untracked files.

        Parameters
        ----------
        asset : Asset
            The asset object.

        Returns
        -------
        dict or None
            The untracked files data if there are any untracked files, otherwise None.
        """
        asset_files = [obj.path for obj in asset.objects]
        all_files = files_at_location(src=asset.repo.fs_path, ignore="*.asset/*")
        all_files = [relative_path(file, asset.repo.fs_path) for file in all_files]
        # compute the diff between the asset files and the filtered files
        diff_files = self.compute_diff(from_objects=asset_files, to_objects=all_files)
        if diff_files.get("added"):
            # filter out added paths based on the .assetignore file
            diff_files["added"] = AssetIgnore(asset.repo.fs_path).filtered_paths(diff_files["added"])
            return diff_files
        return None
