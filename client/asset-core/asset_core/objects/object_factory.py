from typing import Type, Callable

from asset_contents.content_factory import StorageFactory
from asset_core.objects.asset_object import AssetObject
from asset_core.objects.group.group_object import GroupObject
from asset_core.objects.object import Object
from asset_core.objects.object_source import ObjectSource


class ObjectFactory:
    def bulk_create(self, source_data: dict,
                    proxy: bool = False,
                    object_type: str = None,
                    callback: Callable = None,
                    repo_dir: str = None) -> [AssetObject]:
        """Creates and returns list of object

        Parameters
        ----------
        source_data: dict
            {storage_name: [ObjectSource()]}
        proxy: bool
            if to be added as proxy
        object_type: str
            object type
        callback: Callable
            callback function
        repo_dir: str
            directory

        Returns
        -------
        [AssetObject]
        """
        if not source_data:
            return []

        object_sources = self.create_contents(source_data=source_data, proxy=proxy)
        object_klass = self.get_object_class(object_type=object_type)
        return object_klass.bulk_create(factory=self,
                                        sources=object_sources,
                                        callback=callback,
                                        repo_dir=repo_dir)

    def get_object_class(self, object_type: str = None) -> Type[AssetObject]:
        # todo: refactor into plugins
        for klass in self.object_klasses():
            if klass.object_type and klass.object_type == object_type:
                return klass
        # default
        return Object

    def object_klasses(self):
        return [Object, GroupObject]

    def create_contents(self, source_data: dict, proxy: bool = False) -> [ObjectSource]:
        result = []
        for storage_name, object_sources in source_data.items():
            storage_klass = StorageFactory.storage_with_name(name=storage_name)
            content_klass = storage_klass.get_content_class()
            for object_src in object_sources:
                object_src.content = content_klass.create(storage_name=storage_name,
                                                          blob=object_src.blob,
                                                          proxy=proxy)
                result.append(object_src)
        return result

    def parse_sources(self, repo_dir: str,
                      targets: list,
                      proxy: bool = False,
                      dest_dir: str = None,
                      ignore: str = None) -> dict:
        """Parses the targets which includes
        - collecting all files if the target is a directory
        - collecting all blobs/urls if the target is a gs url or web url

        Parameters
        ----------
        repo_dir: str
            repo directory
        targets: [str]
            list of files, urls etc.
        proxy: bool
            if to be added as proxy
        dest_dir: str
            optional, to create a directory and add files in it
        ignore: str

        Returns
        -------
        dict:
            {storage_name: set<ContentSource>()}
        """
        result = {}
        sources = StorageFactory.parse_sources(repo_dir=repo_dir,
                                               targets=targets,
                                               proxy=proxy,
                                               dest_dir=dest_dir,
                                               ignore=ignore)

        for storage_name in sources:
            stored = set()
            object_sources: dict = sources[storage_name]
            for path in object_sources:
                stored.add(ObjectSource(blob=object_sources[path], path=path))
            result[storage_name] = stored
        return result

    def de_serialize(self, asset, data: dict) -> AssetObject:
        object_klass = self.get_object_class(object_type=data.get("object_type"))
        return object_klass.de_serialize(asset=asset, data=data)
