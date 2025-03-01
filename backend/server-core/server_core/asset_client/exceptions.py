"""Exceptions raised by the dvc."""
from typing import List


class AssetException(Exception):
    """Base class for all dvc exceptions."""
    msg = None

    def __init__(self, msg=None, *args):
        self.msg = msg or self.__class__.msg
        if not self.msg and args:
            self.msg = args[0]
        if not self.msg:
            raise Exception("required param missing: msg")
        super().__init__(msg, *args)

    def to_json(self):
        return {"error": self.msg}


class AssetStoreCreateError(Exception):
    """throw if asset store is invalid"""
    pass


class ForbiddenRefError(AssetException):
    pass


class AssetStoreInvalidError(Exception):
    pass


class InvalidArgumentError(ValueError, AssetException):
    """Thrown if arguments are invalid."""
    pass


class InvalidaAssetNameError(AssetException):
    """Thrown if the asset name passed by the user is invalid"""
    msg = "invalid asset name"
    pass


class AssetNotFoundError(AssetException):
    msg = "asset not found locally"
    pass


class InvalidObjectPathError(AssetException):
    msg = "file not found"
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


class InvalidVersionError(AssetException):
    pass

class AssetClassNotFoundError(AssetException):
    pass


class AssetParserError(AssetException):
    """Base class for CLI parser errors."""

    def __init__(self):
        super().__init__("parser error")