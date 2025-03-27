import subprocess

from asset_core.configs import configs
from asset_manager.commands.alias_actions import get_action_group as alias_group
from asset_manager.commands.asset_actions import get_actions as asset_actions
from asset_manager.commands.asset_class_actions import get_action_group as class_group
from asset_manager.commands.auth_actions import get_action_group as auth_group
from asset_manager.commands.config_actions import get_action_group as configs_group
from asset_manager.commands.package_actions import get_action_group as package_group
from asset_manager.commands.parser import CommandParser
from asset_manager.commands.project_actions import get_action_group as projects_group
from asset_manager.commands.refs_actions import get_action_group as refs_group
from asset_manager.commands.store_actions import get_action_group as home_group
from asset_pluggy.storage.storage_factory import StorageFactory


def get_parser(mode: configs.ConfigModes = None) -> CommandParser:
    # turn_off_globbing()
    mode = mode or configs.DEFAULT_MODE
    configs.Configs.shared(mode=mode)
    parser = CommandParser()
    parser.add_actions(*asset_actions())
    parser.add_action_groups(class_group(),
                             auth_group(),
                             home_group(),
                             refs_group(),
                             projects_group(),
                             alias_group(),
                             package_group(),
                             configs_group()
                             )
    return parser


def turn_off_globbing():
    """turn off globbing - this is temp fix instead of adding alias to .bashrc or .zshrc
    it assumes that the user will use atleast another asset command before passing a glob string

    Returns
    -------
    """
    subprocess.run(["set", "-o", "noglob"], check=True, text=True, shell=True)


def print_storages():
    prefixes = ["gs://", "s3://", "gcr.io/", "us.gcr.io/", "file://"]
    for prefix in prefixes:
        print(f"{prefix}: {StorageFactory.storage_with_prefix(prefix=prefix)}")
