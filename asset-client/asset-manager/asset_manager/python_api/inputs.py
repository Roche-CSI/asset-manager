from __future__ import annotations

from typing import TYPE_CHECKING

from asset_core.api.repo_api import AddAPI, InfoAPI
from asset_core.configs import AppSettings
from asset_core.configs import configs
from asset_manager.app import ACTIVE_CONFIG_MODE

if TYPE_CHECKING:
    from asset_manager.python_api.artifact import Artifact

# make sure config mode is set properly
configs.Configs.shared(mode=ACTIVE_CONFIG_MODE)


def filtered_inputs(inputs: dict) -> dict:
    """Filter the inputs dictionary by removing 'dst' from inputs and 'src' from dependents.

    Parameters
    ----------
    inputs : dict
        The input dictionary which contains 'inputs' and 'dependents' as keys.

    Returns
    -------
    dict
        The filtered input dictionary.
    """
    for input_ in inputs.get("inputs", []):
        _ = input_.pop("dst")  # remove the dst from inputs

    for dependent in inputs.get("dependents", []):
        _ = dependent.pop("src")  # remove the src from dependents
    return inputs


class ArtifactInputs:

    def __init__(self, artifact: Artifact):
        """Initialize the ArtifactInputs class.

        Parameters
        ----------
        artifact : Artifact
            The artifact object.
        """
        self._artifact = artifact

    def add(self, input_name: str, label: str) -> dict:
        """Add an input to the artifact.

        Parameters
        ----------
        input_name : str
            The asset_name_version to add as input to the artifact.
        label : str
            The label for the input.

        Returns
        -------
        dict
            The updated list of inputs.
        """
        api = self._artifact._api.add
        with api.environment():
            api.add_ref(src_name=input_name, label=label)
            return self.list()

    def list(self, remote=False, version=None) -> dict:
        """List the inputs of the artifact.

        Parameters
        ----------
        remote : bool, optional
            Whether to list remote inputs, by default, False.
        version : str, optional
            The version of the artifact, by default None.

        Returns
        -------
        dict
            The list of inputs.
        """
        api = self._artifact._api.info
        with api.environment():
            data = api.list_refs(version=version, remote=remote, jsonize=True)
            return filtered_inputs(inputs=data)

    @classmethod
    def remote_add(cls,
                   artifact_name: str,
                   input_name: str,
                   label: str):
        """Add an input to a remote asset.

        Parameters
        ----------
        artifact_name : str
            The target asset_name_version to which the inputs would be added.
        input_name : str
            The asset_name_version to add as input to the target asset.
        label : str
            The label for the input.

        Notes
        ----------
        The artifact_name should be the root version name.
        Currently, we allow adding inputs to the root version only.
        """
        # TODO: expose properties api
        with AppSettings.shared().project_environment(project_id=AppSettings.shared().active_project):
            AddAPI.add_ref_to_remote_asset(src_name=input_name,
                                           dst_name=artifact_name,
                                           label=label)

    @classmethod
    def remote_list(cls, artifact_name: str, version=None) -> dict:
        """List the inputs of a remote artifact.

        Parameters
        ----------
        artifact_name : str
            The target asset_name_version you want to list the inputs for.
        version : str, optional
            The version of the artifact, by default None.

        Returns
        -------
        dict
            The list of inputs.
        """
        artifact_name = f"{AddAPI.asset_name(artifact_name)}/{version}" if version else artifact_name

        with AppSettings.shared().project_environment(project_id=AppSettings.shared().active_project):
            data = InfoAPI.list_remote_refs(asset_name=artifact_name,
                                            project_id=AppSettings.shared().active_project,
                                            jsonize=True)
            return filtered_inputs(inputs=data)
