from asset_core.configs import configs
from asset_manager.app import ACTIVE_CONFIG_MODE
from asset_manager.plugins import register_plugins
from asset_manager.python_api.artifact import Artifact
from asset_manager.python_api.auth import Auth
from asset_manager.python_api.config import Config
from asset_manager.python_api.klass import Klass
from asset_manager.python_api.project import Project
from asset_manager.python_api.store import Store
from asset_utils.utils.log_utils import disable_user_log

# make sure config mode is set properly
configs.Configs.shared(mode=ACTIVE_CONFIG_MODE)


def disable_logging():
    """Disables logging for the asset manager."""
    disable_user_log()


def get(path: str) -> Artifact:
    """Returns the existing artifact object at the given path.

    Parameters
    ----------
    path : str
        The file system path to the artifact.

    Returns
    -------
    Artifact
        The artifact object located at the specified path.
    """
    register_plugins()
    return Artifact(path=path)


def init(class_name: str, path: str, add_files=False) -> Artifact:
    """Creates a new artifact object at the given path.

    Parameters
    ----------
    class_name : str
        The class name of the artifact to be created.
    path : str
        The file system path where the artifact will be created.
    add_files : bool, optional
        Whether to add files to the artifact upon creation, by default False.

    Returns
    -------
    Artifact
        An instance of Artifact. Will throw an error if there is an existing artifact at the path.

    Raises
    ------
    Exception
        If an artifact already exists at the specified path.
    """
    register_plugins()
    return Artifact.create(path=path, class_name=class_name, add_files=add_files)


def get_or_init(class_name: str, path: str, add_files=False) -> Artifact:
    """Returns an existing artifact object at the given path or creates a new artifact object at the path.

    Parameters
    ----------
    class_name : str
        The class name of the artifact to be created.
    path : str
        The file system path where the artifact will be created.
    add_files : bool, optional
        Whether to add files to the artifact upon creation, by default False.

    Returns
    -------
    Artifact
        An instance of Artifact. Will create a new artifact if one does not already exist at the path.

    Notes
    -----
    If an artifact already exists at the specified path, the existing artifact object will be returned.
    """
    register_plugins()
    return Artifact.get_or_create(path=path, class_name=class_name, add_files=add_files)


def clone(name: str, path: str, soft=False, exists_ok=True, credentials: str = None) -> Artifact:
    """Clones an asset and returns the Artifact.

    Parameters
    ----------
    name : str
        The name of the asset to clone.
    path : str
        The location of the asset.
    soft : bool, optional
        Whether to perform a soft clone, by default False.
    exists_ok : bool, optional
        Whether the operation should proceed if the artifact already exists at the target location, by default True.
    credentials : str, optional
            The credential file path to be used for accessing the remote files.

    Returns
    -------
    Artifact
        The cloned artifact object.
    """
    register_plugins()
    return Artifact.clone(name=name, path=path, soft=soft, exists_ok=exists_ok, credentials=credentials)


def clone_or_pull(name: str, path: str, soft=False, force=False) -> Artifact:
    """Clones an asset or pulls the existing asset to the latest version.

    Parameters
    ----------
    name : str
        The name of the asset to clone.
    path : str
        The location of the asset.
    soft : bool, optional
        Whether to perform a soft clone, by default False.
    force : bool, optional
        Whether to force the pull operation, by default False.

    Returns
    -------
    Artifact
        The cloned or pulled artifact object.
    """
    register_plugins()
    return Artifact.clone_or_pull(name=name, path=path, soft=soft, force=force)


def find(class_name: str, alias: str = None, hash: str = None) -> str:
    """Finds an asset given the class name with alias, or hash.

    Parameters
    ----------
    class_name : str, optional
        The class name of the asset, by default None.
    alias : str, optional
        The alias of the asset, by default None.
    hash : str, optional
        The hash of the asset, by default None.

    Returns
    -------
    str
        The name of the found asset.
    """
    register_plugins()
    return Artifact.find(class_name=class_name, hash=hash, alias=alias)


def fetch(asset_name=None, class_name=None, force=False):
    """Fetches metadata of the specified asset from the server.

    Parameters
    ----------
    asset_name : str
        The name of the asset to fetch.
    class_name : str
        The name of the class to fetch all assets for.
    force : bool, optional
        Whether to force the fetch operation, by default False.
    """
    register_plugins()
    Artifact.fetch_asset_class(asset_name=asset_name, class_name=class_name, force=force)


def find_size(asset_version_name: str) -> int:
    """Finds the size of a specified asset version from server.

    Parameters
    ----------
    asset_version_name : str
        The name of the asset version. In <class_name><seq_id><version> format.

    Returns
    -------
    int
        The size of the asset version in bytes.
    """
    register_plugins()
    return Artifact.find_size(asset_version_name=asset_version_name)


def exists(name: str) -> bool:
    """Checks if an asset exists in the asset store.

    Parameters
    ----------
    name : str
        The name of the asset to check.
        Name can be in <class_name>/<seq_id> or <class_name>/<alias> format.
        Name can also include version number in <class_name>/<seq_id>/<version> format.

    Returns
    -------
    bool
        True if the asset exists, False otherwise.
    """
    register_plugins()
    return Artifact.asset_name_exists(name=name)


def copy(src: str, dst: str, recursive=False, force=False, credentials=None):
    """Copy files and objects from source to destination.

    Parameters
    ----------
    src : str
        Source path/URL of the object to copy.
    dst : str
        Destination path/URL where objects would be copied to.
    recursive : bool, optional
        Recursive, use this flag to copy directories, by default False.
    force : bool, optional
        If True, overwrites existing files without asking.
    credentials : str, optional
        path of the gcs/aws credentials to use for copying.
    """
    register_plugins()
    Artifact.copy(src=src, dst=dst, recursive=recursive, force=force, credentials=credentials)


def __getattr__(name):
    """Dynamically returns an object based on the attribute name.

    Parameters
    ----------
    name : str
        The name of the attribute being accessed.

    Returns
    -------
    Project or Auth or Klass
        The corresponding object for the attribute name.

    Raises
    ------
    AttributeError
        If the attribute name does not match the supported ones.

    Notes
    -----
    This method is used to dynamically access project, auth, and klass objects without explicitly
    defining them as attributes of the module.
    https://stackoverflow.com/questions/880530/can-modules-have-properties-the-same-way-that-objects-can
    """
    register_plugins()
    if name == "project":
        return Project()
    if name == "auth":
        return Auth()
    if name == "klass":
        return Klass()
    if name == "store":
        return Store()
    if name == "config":
        return Config()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
