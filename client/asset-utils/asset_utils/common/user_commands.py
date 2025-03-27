from asset_utils.utils.log_utils import colored_string, LogColors

COMMAND_TEMPLATE = "{start}use: {cmd} --> {desc}{end}"
HELP_DESC = "for more details"
COMMAND_COLOR = LogColors.COMMAND

SET_AUTH = {"cmd": "asset auth set <path-gcp-credentials>",
            "desc": "to set the credentials (need to do this only once)"}
SET_USER = {"cmd": "asset auth set --user <username>",
            "desc": "to set the user for asset (need to do this only once)"}

FETCH_ASSET = {"cmd": "asset fetch", "desc": "to refresh the asset metadata from remote"}

LIST_CLASS_ASSETS = {"cmd": "asset list --class <class-name>", "desc": "to list all the assets in a class"}
FETCH_CLASS_ASSETS = {"cmd": "asset fetch --class <class-name>", "desc": "to refresh the assets from remote"}

LIST_CLASSES = {"cmd": "asset class list", "desc": "to list all the asset classes"}
FETCH_CLASSES = {"cmd": "asset class fetch", "desc": "to refresh the asset-classes from remote"}
CREATE_ASSET_CLASS = {"cmd": "asset class init", "desc": "to create asset-class"}

USE_ASSET = "asset use <asset-name>"
INIT_REPO = {"cmd": "asset init <class-name>", "desc": "to initialize an asset of the class"}
CREATE_ASSET = {"cmd": "asset init <class-name>", "desc": "to create an asset in the class"}
DOWNLOAD_ASSET = {"cmd": "asset download", "desc": "to download the missing files"}
DOWNLOAD_ASSET_WITH_CRED = {"cmd": "asset download --cred <filepath>", "desc": "to download using credentials"}
# info
ASSET_INFO = {"cmd": "asset info", "desc": "to view the asset"}
ASSET_INFO_METADATA = {"cmd": "asset info --metadata", "desc": "to view the metadata of the asset"}
ASSET_INFO_ATTRIBUTES = {"cmd": "asset info --attributes", "desc": "to view the attributes of the asset"}

DELETE_ASSET = "asset delete <asset-name>"
UPLOAD_ASSET = {"cmd": "asset upload", "desc": "to update the asset in remote"}
ADD_TO_ASSET = {"cmd": "asset add <file>...", "desc": "to add files, dirs to asset"}
CLONE_ASSET = {"cmd": "asset clone <asset_name>", "desc": "to clone an asset"}
SWITCH_VERSION = {"cmd": "asset switch --version <version>", "desc": "to switch to a different version"}
FETCH_VERSIONS = {"cmd": "asset fetch --versions", "desc": "to fetch the versions of the asset"}
LIST_VERSIONS = {"cmd": "asset versions", "desc": "to list the versions and commits in asset"}
DIFF_VERSIONS = {"cmd": "asset diff <ver>",
                 "desc": "to view the differences between the specified version and current version"}
DIFF_FILE = {"cmd": "asset diff <ver> --file <filepath>",
             "desc": "to view the changes to a file between the specified version and current version"}
# union
UNION_VERSIONS = {"cmd": "asset union <ver>", "desc": "to combine the specified version with the current version"}
UNION_FILE = {"cmd": "asset union <ver> --file <filepath>",
              "desc": "to combine the changes to a file between the specified version and current version"}
UNION_CONTINUE = {"cmd": "asset union --continue <filepath>", "desc": "to complete the union process"}

ASSET_STATUS = {"cmd": "asset status", "desc": "to view any changes to the asset"}
UPDATE_ASSET = {"cmd": "asset update --all", "desc": "to update all un-staged changes"}
UPDATE_OBJECT = {"cmd": "asset update <file>...", "desc": "to update un-staged changes to a file"}
# discard
DISCARD_ASSET = {"cmd": "asset discard --all", "desc": "to discard all staged and unstaged changes"}
DISCARD_STAGED_OBJECT = {"cmd": "asset discard --staged <file>...", "desc": "to discard changes to a file"}
DISCARD_UNSTAGED_OBJECT = {"cmd": "asset discard --unstaged <file>...", "desc": "to discard changes to a file"}
# inputs
INPUTS_ADD = {"cmd": "asset inputs add <input_name> --label <label_name>",
              "desc": "to add an input to the current asset (from inside the asset dir)"}
INPUTS_ADD_REMOTE = {"cmd": "asset inputs add <input_name> --remote <asset_name> --label <label_name>",
                     "desc": "to add an input to a remote asset (from anywhere)"}
INPUTS_INFO = {"cmd": "asset inputs info", "desc": "to view the inputs for an asset (from inside the asset dir)"}
INPUTS_INFO_REMOTE = {"cmd": "asset inputs info --name <asset_name>",
                      "desc": "to view the inputs for an asset (from anywhere)"}
INPUTS_INFO_VERSION = {"cmd": "asset inputs info --version <version>",
                       "desc": "to view the inputs of any version (from inside asset dir)"}
# alias
ALIAS_SET = {"cmd": "asset alias set <alias>",
             "desc": "to add an alias to your asset - an alias is a user defined primary key for an asset"}
ALIAS_REMOVE = {"cmd": "asset alias remove", "desc": "to remove an alias from your asset"}
ALIAS_INFO = {"cmd": "asset alias info", "desc": "to view information about the alias for your asset"}

COMPUTE_HASH = {"cmd": "asset hash <src>", "desc": "to compute the hash for a file/gs/gcr url"}
# auth
USER_LOGIN = {"cmd": "asset auth login", "desc": "to login and use asset-manager"}
USER_TOKEN = {"cmd": "asset auth info --token", "desc": "to view the access token for the user"}
# projects
ACTIVATE_PROJECT = {"cmd": "asset project activate <project_name>", "desc": "to activate a project"}
LIST_PROJECTS = {"cmd": "asset project list", "desc": "to list all projects you have access to"}
# signing in
USER_SIGNUP = {"cmd": "asset auth signup --user <id> --email <email>",
               "desc": "to signup with asset-manager (first-time users)"}
# store
ASSET_STORE_SET = {"cmd": "asset store set <path-to-directory>", "desc": "to set the asset-store directory"}
ASSET_STORE_INFO = {"cmd": "asset store info", "desc": "to view the path to the asset-store"}
ASSET_STORE_CLEAR = {"cmd": "asset store clear", "desc": "to clear the asset-store and all its contents"}
ASSET_STORE_PRUNE = {"cmd": "asset store prune", "desc": "to remove all invalid assets from the asset-store"}

VIEW_USER_CONFIGS = {"cmd": "asset config info",
                     "desc": "to view the custom configurations that can be set by the user"}
SET_USER_CONFIGS = {"cmd": "asset config set --key <config_key> --value <config_value>",
                    "desc": "to set customize configurations to your requirements"}
RESET_USER_CONFIGS = {"cmd": "asset config reset --key <config_key>",
                      "desc": "to reset any configuration to factory defaults"}


def formatted(command: dict, color):
    return COMMAND_TEMPLATE.format(
        start="(",
        cmd=colored_string(command.get('cmd'), color=color),
        desc=command.get('desc'),
        end=")",
    )


class UserCommands:

    def list_assets(self, color=COMMAND_COLOR):
        return formatted(LIST_CLASS_ASSETS, color=color)

    def list_classes(self, color=COMMAND_COLOR):
        return formatted(LIST_CLASSES, color=color)

    def list_help(self, color=COMMAND_COLOR):
        return formatted({"cmd": "asset list --help", "desc": HELP_DESC}, color)

    def fetch_asset(self, color=COMMAND_COLOR):
        return formatted(FETCH_ASSET, color=color)

    def fetch_assets(self, color=COMMAND_COLOR):
        return formatted(FETCH_CLASS_ASSETS, color)

    def fetch_classes(self, color=COMMAND_COLOR):
        return formatted(FETCH_CLASSES, color=color)

    def fetch_help(self, color=COMMAND_COLOR):
        return formatted({"cmd": "asset fetch --help", "desc": HELP_DESC}, color)

    def use_asset(self, color=COMMAND_COLOR):
        return colored_string(USE_ASSET, color=color)

    def init_repo(self, color=COMMAND_COLOR):
        return formatted(INIT_REPO, color=color)

    def create_asset(self, color=COMMAND_COLOR):
        return formatted(CREATE_ASSET, color=color)

    def create_asset_class(self, color=COMMAND_COLOR):
        return formatted(CREATE_ASSET_CLASS, color=color)

    def download_asset(self, with_credential=False, color=COMMAND_COLOR):
        cmd = DOWNLOAD_ASSET_WITH_CRED if with_credential else DOWNLOAD_ASSET
        return formatted(cmd, color=color)

    def asset_info(self, color=COMMAND_COLOR):
        return formatted(ASSET_INFO, color=color)

    def asset_info_metadata(self, color=COMMAND_COLOR):
        return formatted(ASSET_INFO_METADATA, color=color)

    def asset_info_attributes(self, color=COMMAND_COLOR):
        return formatted(ASSET_INFO_ATTRIBUTES, color=color)

    def delete_asset(self, color=COMMAND_COLOR):
        return colored_string(DELETE_ASSET, color=color)

    def set_auth(self, color=COMMAND_COLOR):
        return formatted(SET_AUTH, color=color)

    def set_user(self, color=COMMAND_COLOR):
        return formatted(SET_USER, color=color)

    def upload_asset(self, color=COMMAND_COLOR):
        return formatted(UPLOAD_ASSET, color=color)

    def add_to_asset(self, color=COMMAND_COLOR):
        return formatted(ADD_TO_ASSET, color=color)

    def clone_asset(self, color=COMMAND_COLOR):
        return formatted(CLONE_ASSET, color)

    def switch_asset_version(self, color=COMMAND_COLOR):
        return formatted(SWITCH_VERSION, color)

    def set_asset_store(self, color=COMMAND_COLOR):
        return formatted(ASSET_STORE_SET, color)

    def asset_store_info(self, color=COMMAND_COLOR):
        return formatted(ASSET_STORE_INFO, color)

    def asset_store_clear(self, color=COMMAND_COLOR):
        return formatted(ASSET_STORE_CLEAR, color)

    def asset_store_prune(self, color=COMMAND_COLOR):
        return formatted(ASSET_STORE_PRUNE, color)

    def asset_status(self, color=COMMAND_COLOR):
        return formatted(ASSET_STATUS, color)

    def update_asset(self, color=COMMAND_COLOR):
        return formatted(UPDATE_ASSET, color)

    def update_object(self, color=COMMAND_COLOR):
        return formatted(UPDATE_OBJECT, color)

    def discard_asset(self, color=COMMAND_COLOR):
        return formatted(DISCARD_ASSET, color)

    def discard_staged_object(self, color=COMMAND_COLOR):
        return formatted(DISCARD_STAGED_OBJECT, color)

    def discard_unstaged_object(self, color=COMMAND_COLOR):
        return formatted(DISCARD_UNSTAGED_OBJECT, color)

    def fetch_versions(self, color=COMMAND_COLOR):
        return formatted(FETCH_VERSIONS, color)

    def list_versions(self, color=COMMAND_COLOR):
        return formatted(LIST_VERSIONS, color)

    def diff_versions(self, color=COMMAND_COLOR):
        return formatted(DIFF_VERSIONS, color)

    def diff_file(self, color=COMMAND_COLOR):
        return formatted(DIFF_FILE, color)

    def union_versions(self, color=COMMAND_COLOR):
        return formatted(UNION_VERSIONS, color)

    def union_file(self, color=COMMAND_COLOR):
        return formatted(UNION_FILE, color)

    def union_continue(self, color=COMMAND_COLOR):
        return formatted(UNION_CONTINUE, color)

    def inputs_add(self, color=COMMAND_COLOR):
        return formatted(INPUTS_ADD, color)

    def inputs_add_remote(self, color=COMMAND_COLOR):
        return formatted(INPUTS_ADD_REMOTE, color)

    def inputs_info(self, color=COMMAND_COLOR):
        return formatted(INPUTS_INFO, color)

    def inputs_info_remote(self, color=COMMAND_COLOR):
        return formatted(INPUTS_INFO_REMOTE, color)

    def inputs_info_version(self, color=COMMAND_COLOR):
        return formatted(INPUTS_INFO_VERSION, color)

    def compute_hash(self, color=COMMAND_COLOR):
        return formatted(COMPUTE_HASH, color)

    def user_login(self, color=COMMAND_COLOR):
        return formatted(USER_LOGIN, color)

    def user_token(self, color=COMMAND_COLOR):
        return formatted(USER_TOKEN, color)

    def activate_project(self, color=COMMAND_COLOR):
        return formatted(ACTIVATE_PROJECT, color)

    def list_projects(self, color=COMMAND_COLOR):
        return formatted(LIST_PROJECTS, color)

    def user_signup(self, color=COMMAND_COLOR):
        return formatted(USER_SIGNUP, color)

    def configs_info(self, color=COMMAND_COLOR):
        return formatted(VIEW_USER_CONFIGS, color)

    def set_user_configs(self, color=COMMAND_COLOR):
        return formatted(SET_USER_CONFIGS, color)

    def reset_user_configs(self, color=COMMAND_COLOR):
        return formatted(RESET_USER_CONFIGS, color)

    def alias_set(self, color=COMMAND_COLOR):
        return formatted(ALIAS_SET, color)

    def alias_remove(self, color=COMMAND_COLOR):
        return formatted(ALIAS_REMOVE, color)

    def alias_info(self, color=COMMAND_COLOR):
        return formatted(ALIAS_INFO, color)
