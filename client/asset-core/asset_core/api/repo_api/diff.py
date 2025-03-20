from __future__ import annotations

import enum
import os
import tempfile

from asset_core.api.repo_api.repo import RepoAPI
from asset_core.asset.asset_diff import AssetDiff
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.objects.asset_object import AssetObject
from asset_utils.utils import web_utils
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LogColors, colored_string
from asset_utils.utils.progress import Progress


class DiffSymbols(enum.Enum):
    ADDED = "[+]"
    REMOVED = "[-]"
    ALTERED = "[*]"
    COMMENT = "#"
    ALL_ADDED = "[all]:[+]"
    ALL_REMOVED = "[all]:[-]"
    ALL_ALTERED = "[all]:[*]"


class DiffApi(RepoAPI):

    def diff(self, file: str = None, src_ver: str = None, dst_ver: str = None, html: bool = False):
        if not src_ver and not dst_ver:
            self.user_log.error("missing required params: src_ver or dst_ver")
            return

        if file:
            self.file_diff(filepath=file, src_ver=src_ver, dst_ver=dst_ver, html=html)
        else:
            self.version_diff(src_ver=src_ver, dst_ver=dst_ver, html=html)

    def version_diff(self, src_ver: str, dst_ver: str, html: bool):
        pbar = Progress.status_bar(desc=f"creating meta information for versions: {src_ver}, {dst_ver}")
        added, removed, altered = self.generate_version_diff(src_ver=src_ver, dst_ver=dst_ver)
        pbar.close(message="done")
        self.print_delta(delta={
            "added": added,
            "removed": removed,
            "altered": altered
        }, src_ver=src_ver, dst_ver=dst_ver)

    def generate_version_diff(self, src_ver: str, dst_ver: str):
        """generates diff between two versions of the asset

        Parameters
        ----------
        src_ver
        dst_ver

        Returns
        -------

        """
        src_ver = src_ver or self.asset.version.number
        dst_ver = dst_ver or self.asset.version.number

        if src_ver == dst_ver:
            self.user_log.message(f"no changes detected between: {src_ver} {dst_ver}")
            return

        src_objects: [str] = [obj.id for obj in self.asset.list_objects(ver_number=src_ver)]
        dst_objects: [str] = [obj.id for obj in self.asset.list_objects(ver_number=dst_ver)]

        delta = AssetDiff().compute_diff(from_objects=src_objects, to_objects=dst_objects)
        added, removed, altered = AssetDiff().file_changed(patch=delta)
        return added, removed, altered

    def print_delta(self, delta: dict, src_ver: str, dst_ver: str):
        columns = {
            "section": "",
            "details": "",
        }
        title = f"asset: {self.asset.name}\n"
        title += f"diff: changes in [{dst_ver}] from [{src_ver}]\n"
        title += f"legends: " \
                 f"{colored_string(f'{DiffSymbols.ADDED.value} - {DiffSymbols.ADDED.name}', color=LogColors.green)} " \
                 f"{colored_string(f'{DiffSymbols.REMOVED.value} - {DiffSymbols.REMOVED.name}', color=LogColors.red)} " \
                 f"{colored_string(f'{DiffSymbols.ALTERED.value} - {DiffSymbols.ALTERED.name}', color=LogColors.yellow)}\n"

        self.user_log.message(title)
        table = []
        table += [
            {
                "section": colored_string(f"{DiffSymbols.ADDED.value}: ", LogColors.green),
                "details": colored_string(obj, LogColors.green)
            } for obj in delta.get("added")
        ]
        table += [
            {
                "section": colored_string(f"{DiffSymbols.REMOVED.value}: ", LogColors.red),
                "details": colored_string(obj, LogColors.red)
            } for obj in delta.get("removed")
        ]
        table += [
            {
                "section": colored_string(f"{DiffSymbols.ALTERED.value}: ", LogColors.yellow),
                "details": colored_string(obj, LogColors.yellow)
            } for obj in delta.get("altered")
        ]
        self.user_log.table(columns=columns, rows=table, table_fmt="plain")
        return True

    def file_diff(self, filepath: str, src_ver: str, dst_ver: str, html: bool = False):
        src_ver = src_ver or self.asset.version.number
        dst_ver = dst_ver or self.asset.version.number
        norm_path = os.path.relpath(os.path.abspath(filepath), start=self.asset.repo.fs_path)
        src_obj: AssetObject = self.asset.get_object(object_path=norm_path, ver_number=src_ver)
        dst_obj: AssetObject = self.asset.get_object(object_path=norm_path, ver_number=dst_ver)
        # if any of the objects are missing, i.e. either the object was added or deleted
        if not src_obj and not dst_obj:
            self.user_log.message(f"{norm_path} not found in {src_ver} or {dst_ver}", color=LogColors.INFO)
            return

        if not src_obj:
            self.user_log.message(f"{norm_path} is missing in {src_ver}, this file was added in {dst_ver}",
                                  color=LogColors.INFO)
            return

        if not dst_obj:
            self.user_log.message(f"{norm_path} is missing in {dst_ver}, this file was deleted in {dst_ver}",
                                  color=LogColors.INFO)
            return

        temp_dir = tempfile.mkdtemp()
        tf = os.path.join(temp_dir, "diff.html")
        desc = {
            "title": {"name": "asset", "val": self.asset.name},
            "subtitle": {"name": "file", "val": norm_path},
            "from_desc": f"version: {src_ver}",
            "to_desc": f"version: {dst_ver}"
        }
        self.download_if_not_exists(contents=[src_obj.content, dst_obj.content])
        if src_obj.content.cache_path == dst_obj.content.cache_path:
            self.user_log.message(f"no differences found: {norm_path}", color=LogColors.INFO)
            return
        try:
            if html:
                templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
                html_file = os.path.join(templates_dir, "diff_template.html")
                css_file = os.path.join(templates_dir, "diff_style.css")
                FileUtils.diff_file_html(from_file=src_obj.content.cache_path,
                                         to_file=dst_obj.content.cache_path,
                                         diff_file=tf,
                                         html_template=html_file,
                                         css_path=css_file,
                                         desc=desc)
                web_utils.open_in_browser(tf)
            else:
                diffs = FileUtils.diff_file(from_file=src_obj.content.cache_path,
                                            to_file=dst_obj.content.cache_path,
                                            from_desc=src_ver,
                                            to_desc=dst_ver)
                self.user_log.message(diffs)
        except UnicodeDecodeError:
            self.user_log.message(f"unable to decode file: {norm_path}", LogColors.ERROR)

    def download_if_not_exists(self, contents: list):
        targets = [content for content in contents if not os.path.exists(content.cache_path)]
        if not targets:
            return
        # download contents
        pbar = Progress.progress_bar(desc="downloading missing files", total=len(targets))
        fetcher = AssetFetcher(store=self.asset.repo.store)
        fetcher.download_contents(contents=contents)
        pbar.close(message="done")
