from functools import cached_property

from asset_core.configs import configs
from asset_manager import ArtifactInputs, Artifact
from asset_manager.app import ACTIVE_CONFIG_MODE
from asset_utils.common import exceptions

# make sure config mode is set properly
configs.Configs.shared(mode=ACTIVE_CONFIG_MODE)


class RefInputs:
    """A way to interact with the inputs of an asset.

    Will use ArtifactInputs to interact with the inputs of the asset.
    """

    def __init__(self, asset_version_name: str):
        self._asset_version_name = asset_version_name

    def list(self) -> dict:
        """List the inputs of the asset from remote.

        Returns
        -------
        dict
            The list of inputs.
        """
        return ArtifactInputs.remote_list(self._asset_version_name)

    def add(self, input_name: str, label: str) -> None:
        """Add an input to the asset remotely.

        Parameters
        ----------
        input_name : str
            The asset_name_version to add as input to the asset.
        label : str
            The label for the input.
        """
        ArtifactInputs.remote_add(artifact_name=self._asset_version_name,
                                  input_name=input_name,
                                  label=label)


class ArtifactRef:
    """A reference to an artifact in the asset manager.

    Will act like a proxy to the artifact. So, no need to have the artifact locally.
    Only be used to call remote functions on the artifact.
    """

    def __init__(self, asset_version_name: str):
        parts = asset_version_name.split("/")
        if len(parts) != 3:
            raise exceptions.InvalidAssetNameError(
                "Invalid asset version name, expected <class_name>/<seq_id>/<version>")
        self.asset_version_name = asset_version_name
        self.asset_name = f"{parts[0]}/{parts[1]}"
        self.active_version = parts[2]

    @cached_property
    def size(self) -> int:
        """The size of the asset version in bytes."""
        return Artifact.find_size(self.asset_version_name)

    @cached_property
    def inputs(self):
        """A way to interact with the inputs of the asset."""
        return RefInputs(self.asset_version_name)

    def exists(self) -> bool:
        """Check if the asset exists."""
        return Artifact.asset_name_exists(self.asset_version_name)
