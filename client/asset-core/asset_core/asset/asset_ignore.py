import os

import pathspec

from asset_core.asset import Asset
from asset_utils.common import exceptions
from asset_utils.utils.log_utils import LoggingMixin

ASSET_IGNORE_FILE_NAME = ".assetignore"


class AssetIgnore(LoggingMixin):
    """Class to handle the assetignore file"""

    def __init__(self, path: str):
        self.ignore_file = path
        # if path is a directory, append the ignore file name
        if not self.ignore_file.endswith(ASSET_IGNORE_FILE_NAME):
            self.ignore_file = os.path.join(self.ignore_file, ASSET_IGNORE_FILE_NAME)
        # the pathspec object to match the ignore patterns
        self._ignore_spec = self.parse_assetignore()

    def parse_assetignore(self):
        """Parse the .assetignore file and return the PathSpec object.

        Returns
        -------
        pathspec.PathSpec
            The pathspec object containing the patterns to ignore.
        """
        try:
            with open(self.ignore_file, "r") as file:
                return pathspec.PathSpec.from_lines("gitwildmatch", file)
        except FileNotFoundError:
            # no .assetignore file means no patterns to ignore
            return None
        except Exception as e:
            raise exceptions.AssetException(f"Error reading .assetignore file: {e}")

    def filtered_paths(self, file_paths: list) -> list:
        """Remove files that match the assetignore patterns.

        Parameters
        ----------
        file_paths : list
            File paths to filter.

        Returns
        -------
        list
            File paths that do not match patterns in the assetignore file.
        """
        if not file_paths or not self._ignore_spec:
            # no paths to filter or no ignore patterns
            return file_paths

        return [file for file in file_paths if not self._ignore_spec.match_file(file)]

    def ignored_paths(self, file_paths: list) -> list:
        """Filter files matching the assetignore patterns.

        Parameters
        ----------
        file_paths : list
            File paths to filter.

        Returns
        -------
        list
            File paths that match patterns in the assetignore file.
        """
        if not file_paths or not self._ignore_spec:
            # no paths to filter or no ignore patterns
            return []

        return [file for file in file_paths if self._ignore_spec.match_file(file)]

    def filter_sources(self, sources: set, asset: Asset, print_log=True) -> set:
        """Filter the sources based on the assetignore file.

        Use this method to filter the sources before adding them to the asset.

        Parameters
        ----------
        sources : set
            The sources to filter.
        asset : Asset
            The asset to which the sources will be added.
        print_log : bool, optional
            Whether to print the ignored paths and user hint. Default is True.

        Returns
        -------
        set
            The filtered sources.
        """
        # split the sources into existing and new sources
        asset_file_paths = set([obj.path for obj in asset.objects])
        existing_sources, new_sources = set(), set()
        for obj in sources:
            if obj.path_in_asset in asset_file_paths:
                existing_sources.add(obj)
            else:
                new_sources.add(obj)

        # filter out the ignored paths from the new sources
        new_source_paths = [obj.path_in_asset for obj in new_sources]
        ignored_paths = self.ignored_paths(new_source_paths)

        if ignored_paths:
            if print_log:
                # print the ignored paths and user hint
                self.user_log.alert("The following paths are ignored by your .assetignore file:")
                self.user_log.info("\n".join(ignored_paths))
                self.user_log.info("hint: Use --force if you really want to add them.")

            # filtered_paths = new_source_paths - ignored_paths
            filtered_paths = set(self.filtered_paths(new_source_paths))
            filtered_sources = [obj for obj in new_sources if obj.path_in_asset in filtered_paths]
            # update the sources with filtered sources
            existing_sources.update(filtered_sources)
            return existing_sources

        # no ignored paths, return the original sources
        return sources
