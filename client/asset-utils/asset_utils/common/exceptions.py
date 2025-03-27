from functools import cached_property

from asset_utils.utils.log_utils import LogData, colored_string, LogColors


class AssetException(Exception):
    """Base class for all asset exceptions."""
    msg: str = None
    data: dict = None
    fatal: bool = True

    def __init__(self, msg=None, data=None, fatal=True, *args):
        self.msg = msg or self.__class__.msg
        if not self.msg and args:
            self.msg = args[0]
        self.data = data or self.__class__.data
        self.fatal = fatal
        if not self.msg:
            raise Exception("required param missing: msg")
        super().__init__(msg, data, *args)

    @cached_property
    def logs(self):
        return LogData()

    @cached_property
    def log_colors(self):
        return LogColors

    def stop_execution(self):
        self.__class__.stop_process()

    def __str__(self):
        msg = colored_string(f"error: {self.msg}", LogColors.ALERT)
        extras = self.logs.print_format()
        if extras:
            msg += f"\n{extras}" if msg else extras
        return msg

    @classmethod
    def stop_process(cls):
        exit(1)


class AssetObjectConflictException(AssetException):
    def __init__(self, b1, b2):
        msg = f'Input type `{b1.unit}` provided by {b1.__name__} already registered by {b2.__name__}'
        super().__init__(msg=msg)


class InvalidStorageURLError(AssetException):
    msg = "Invalid storage url"


class InvalidStorageBackendError(AssetException):
    msg = "Invalid storage backend, this blob store is not supported"


class InvalidStorageCredentialsError(AssetException):
    msg = "Invalid storage credentials, please check your credentials and try again"


class NoActiveProjectError(AssetException):
    msg = "There is no active project set, please select an active project"


class InvalidProjectError(AssetException):
    msg = "project not found"


class InvalidRemoteURLError(AssetException):
    msg = "remote_url is missing, please login again to retry"


class RemoteStorageError(AssetException):
    msg = "remote storage for asset not configured yet"


class InvalidCredentialError(AssetException):
    msg = "Invalid application credentials, please sign-in to update your credentials"


class InsufficientCredentialError(AssetException):
    msg = "You don't have sufficient permission to perform this operation"


class ContentNotAvailableError(AssetException):
    msg = "Content not available locally"


class ForbiddenRefError(AssetException):
    """thrown in case of forbidden references for example,
    self refs
    """
    pass


class InvalidAliasError(AssetException):
    pass


class InvalidTagError(AssetException):
    pass


class AssetStoreCreateError(AssetException):
    """throw if asset store is invalid"""
    pass


class AssetStoreInvalidError(AssetException):
    pass


class InvalidArgumentError(ValueError, AssetException):
    """Thrown if arguments are invalid."""
    pass


class InvalidAssetNameError(AssetException):
    """Thrown if the asset name passed by the user is invalid"""
    msg = "invalid asset name"
    pass


class AssetNotFoundError(AssetException):
    msg = "asset not found locally"
    pass


class InvalidObjectSourceError(AssetException):
    msg = "file not found"
    pass


class UnSupportedOperation(AssetException):
    pass


class StagePathAsOutputError(AssetException):
    """Thrown if directory that stage is going to be saved in is specified as
    an output of another stage.

    Args:
        stage (Stage): a stage that is in some other stages output
        output (str): an output covering the stage above
    """

    def __init__(self, stage, output):
        assert isinstance(output, str)
        super().__init__(
            "{stage} is within an output '{output}' of another stage".format(
                stage=stage, output=output
            )
        )


class CircularDependencyError(AssetException):
    """Thrown if a file/directory specified both as an output and as a
    dependency.

    Args:
        dependency (str): path to the dependency.
    """

    def __init__(self, dependency):
        assert isinstance(dependency, str)

        msg = "'{}' is specified as an output and as a dependency."
        super().__init__(msg.format(dependency))


class ArgumentDuplicationError(AssetException):
    """Thrown if a file/directory is specified as a dependency/output more
    than once.

    Args:
        path (str): path to the file/directory.
    """

    def __init__(self, path):
        assert isinstance(path, str)
        super().__init__(f"file '{path}' is specified more than once.")


class MoveNotDataSourceError(AssetException):
    """Thrown when trying to move a file/directory that is not an output
    in a data source stage.

    Args:
        path (str): path to the file/directory.
    """

    def __init__(self, path):
        msg = (
            "move is not permitted for stages that are not data sources. "
            "You need to either move '{path}' to a new location and edit "
            "it by hand, or remove '{path}' and create a new one at the "
            "desired location."
        )
        super().__init__(msg.format(path=path))


class NotAssetRepoError(AssetException):
    """Thrown if a directory is not a BaseAsset repo"""
    pass


class DuplicateRepoError(AssetException):
    """Thrown if two repos with the same id exist """
    msg = "Multiple repos found with the same repo id"


class RepoOverwriteError(AssetException):
    msg = "Possible Repo override detected - existing repo id found"


class RepoMovedError(AssetException):
    msg = "Repo was moved from its original location"


class NestedRepoError(AssetException):
    msg = "Nested repo detected"


class InvalidVersionError(AssetException):
    pass


class InvalidSeqIdError(AssetException):
    pass


class InvalidInputError(AssetException):
    pass


class ServerNotAvailableError(AssetException):
    pass


class ServerUrlNotSetError(AssetException):
    msg = "asset-server URL not set"


class ResourceDownloadError(AssetException):
    msg = "failed to download resource"


class InvalidRefError(AssetException):
    pass


class AssetClassNotFoundError(AssetException):
    msg = "asset class not found"


class ClassListNotFoundError(AssetException):
    msg = "asset-class list not found"


class IncorrectServerResponseError(AssetException):
    pass


class AssetParserError(AssetException):
    """Base class for CLI parser errors."""

    def __init__(self):
        super().__init__("parser error")


class BackoffRetryError(AssetException):
    msg = "retry immediately"


class GroupRetryError(AssetException):
    msg = "retry in group"


class ReadOnlyAssetError(AssetException):
    msg = "read-only asset, change tracking and updates are disabled"


class AssetSnapshotError(AssetException):
    msg = "error while handling asset snapshot"
