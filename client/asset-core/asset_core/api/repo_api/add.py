import functools

from asset_core.asset import Asset
from asset_core.asset.asset_ignore import AssetIgnore
from asset_core.asset.asset_version import ROOT_VERSION_NUMBER
from asset_core.asset.refs.asset_ref import AssetRef
from asset_core.objects.group.group_object import GroupObject
from asset_core.objects.object_factory import ObjectFactory
from asset_core.store import AssetStore
from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils import is_integer, contains_special_chars
from asset_utils.utils.log_utils import colored_string, LogColors
from asset_utils.utils.progress import Progress
from .info import InfoAPI
from .repo import RepoAPI

ALLOWED_OBJECT_TYPES = ["group"]
MAX_ALLOWED_TAGS = 10
MAX_TAG_LENGTH = 20


class AddAPI(RepoAPI):

    def __init__(self, repo):
        super().__init__(repo=repo)

    def add_title(self, title: str):
        """Adds a title to the asset."""
        title = title.strip()
        self.asset.title = title
        self.user_log.info(f"added title: {title}")
        self.user_log.message(UserCommands().upload_asset())

    def add_description(self, description: str):
        """Adds a description to the asset."""
        description = description.strip()
        self.asset.description = description
        self.user_log.info(f"added description: {description}")
        self.user_log.message(UserCommands().upload_asset())

    def add_metadata(self, metadata: dict):
        """Adds metadata to the asset."""
        self.asset.metadata = metadata
        self.user_log.info(f"added metadata to the asset")
        self.user_log.message(UserCommands().upload_asset())

    def add_attributes(self, attributes: dict):
        """Adds attributes to the asset."""
        self.asset.attributes = attributes
        self.user_log.info(f"added attributes to the asset")
        self.user_log.message(UserCommands().upload_asset())

    def add_tags(self, tags: [str]):
        """Adds tags to the asset tags list.
        - allow max 10 tags
        """
        tags = [tag.strip() for tag in tags]
        # remove duplicates
        tags = set(tags)
        for tag in tags:
            self.validate_tag(tag)

        updated_tags = set(self.asset.tags).union(tags)
        if len(updated_tags) > MAX_ALLOWED_TAGS:
            raise exceptions.InvalidTagError(f"a maximum of {MAX_ALLOWED_TAGS} tags is allowed")
        # update the asset tags
        self.asset.tags = list(updated_tags)
        self.user_log.info(f"asset tags: {self.asset.tags}")
        self.user_log.message(UserCommands().upload_asset())

    def validate_tag(self, tag: str) -> None:
        """Checks if the tag is valid.
        - max len 20 chars
        - only lowercase and digits
        - not integer or float
        - no special chars except '_', '.', '-'
        """
        if not tag:
            raise exceptions.InvalidTagError("missing tag")
        if len(tag) > MAX_TAG_LENGTH:
            raise exceptions.InvalidTagError("tag length must be less than 20 characters")
        if not tag.islower():
            raise exceptions.InvalidTagError("tag must be in lowercase")
        if is_integer(tag):
            raise exceptions.InvalidTagError("tag cannot be an integer")
        if contains_special_chars(tag):
            raise exceptions.InvalidTagError("tag cannot contain any special characters other than '_', '.', '-'")

    def add_ref(self, src_name: str,
                label: str,
                properties: dict = None):
        # TODO: check env_var to confirm if adding refs to non root version is allowed
        if self.asset.version.number != ROOT_VERSION_NUMBER:
            user_input = self.user_log.ask_user(
                question=f"you are currently in version: {self.asset.version.number}. but you are only allowed to "
                         f"add inputs to root version.\ndo you want to add the input to the root version?",
                options=["y", "n"],
                default="y"
            )
            if user_input.lower() != "y":
                self.user_log.message("operation aborted", LogColors.ALERT)
                return
        self.add_ref_to_asset(asset=self.asset,
                              src_name=src_name,
                              label=label,
                              properties=properties)

    def add_ref_to_asset(self, asset: Asset,
                         src_name: str,
                         label: str,
                         properties: dict = None):
        """Add a reference to the current asset.

        Parameters
        ----------
        asset : Asset
            The asset to which the reference will be added.
        src_name : str
            The source name of the reference.
        label : str
            The label for the reference.
        properties : dict, optional
            Additional properties for the reference.

        Raises
        ------
        exceptions.ForbiddenRefError
            If the reference is forbidden.
        exceptions.AssetException
            If there is an error adding the reference.
        """
        try:
            added, existing = asset.create_and_add_ref(
                src_name=src_name,
                label=label,
                properties=properties
            )
            msg = ""
            if added:
                msg += colored_string("success\n", LogColors.SUCCESS)
                msg += colored_string(f"input added: {','.join([ref.src_version.get('name') for ref in added])}",
                                      color=LogColors.INFO)
            if existing:
                msg += colored_string("input already exists, so not added again\n", LogColors.INFO)
                msg += f"already exists: {','.join([ref.src_version.get('name') for ref in existing])}"
            self.user_log.message(msg)
            InfoAPI(asset=asset).list_refs()
            self.user_log.message(UserCommands().upload_asset())
        except exceptions.ForbiddenRefError as e:
            e.logs.add("please choose a different input to add to the asset inputs", LogColors.INFO)
            e.logs.add(UserCommands().inputs_add())
            raise
        except exceptions.AssetException:
            raise

    @classmethod
    def add_ref_to_remote_asset(cls, src_name: str,
                                label: str,
                                dst_name: str = None,
                                properties: dict = None,
                                asset: Asset = None):
        """Adds a ref/input directly to a remote asset.

        There are two possible scenarios:
        - The remote asset is not available locally.
        - The user may have the asset locally but wants to add a ref/input directly in remote instead of add and upload.

        Parameters
        ----------
        src_name : str
            The source name of the ref/input.
        label : str
            The label for the ref/input.
        dst_name : str, optional
            The destination name of the ref/input.
        properties : dict, optional
            Additional properties for the ref/input.
        asset : Asset, optional
            The asset to which the reference will be added.

        Raises
        ------
        exceptions.AssetException
            If both `dst_name` and `asset` are None.
        exceptions.ForbiddenRefError
            If the asset is trying to reference itself.
        """
        if not dst_name and not asset:
            raise exceptions.AssetException("both dst_name and asset can not be None")

        if dst_name and len(dst_name.split("/")) == 3:
            dst_class, dst_seq, dst_version = dst_name.split("/")
            if dst_version != ROOT_VERSION_NUMBER:
                user_input = cls.user_log.ask_user(
                    question=f"you are trying to add input to version: {dst_version}. but you are only allowed to "
                             f"add inputs to the root version.\ndo you want to add the input to the root version?",
                    options=["y", "n"],
                    default="y"
                )
                if user_input.lower() != "y":
                    cls.user_log.message("operation aborted", LogColors.ALERT)
                    return
                dst_name = f"{dst_class}/{dst_seq}/{ROOT_VERSION_NUMBER}"

        dst_id = None
        if not dst_name:
            target = asset.root_version()  # only add inputs to root version
            dst_name = target.name
            dst_id = target.id

        # check if the asset is trying to reference itself
        if cls.asset_name(src_name) == cls.asset_name(dst_name):
            raise exceptions.ForbiddenRefError(
                f"can not create input: {src_name}, asset can not reference itself")

        project_id = asset.asset_class.project if asset else AssetStore.shared().project_id
        try:
            ref = AssetRef.create(src_ver_name=src_name,
                                  dst_ver_name=dst_name,
                                  dst_ver_id=dst_id,
                                  label=label,
                                  properties=properties,
                                  project_id=project_id,
                                  remote=True)
            # todo: if adding to current asset, we need to update the asset also
            if ref:
                cls.user_log.message("success, input created", LogColors.SUCCESS)
                InfoAPI.print_refs([ref])
            else:
                cls.user_log.message("error, unable to create input", LogColors.ALERT)
        except exceptions.AssetException:
            raise

    @classmethod
    def asset_name(cls, name: str):
        if not name:
            raise exceptions.AssetException("missing asset name")
        parts = name.split("/")
        if len(parts) < 2:
            raise exceptions.AssetException("invalid asset name")
        return f"{parts[0]}/{parts[1]}"

    def add_alias(self, alias: str):
        # remove leading and trailing whitespaces
        alias = alias.strip()
        # check if the alias is valid
        self.validate_alias(alias)
        self.asset.alias = alias
        InfoAPI(asset=self.asset).list_alias()

    def validate_alias(self, alias: str) -> None:
        """Validates the alias for the asset.

        Raises
        ------
        exceptions.InvalidAliasError
            If the alias is invalid
        """
        if not alias:
            raise exceptions.InvalidAliasError("missing alias")
        # must not be an integer
        if is_integer(alias):
            raise exceptions.InvalidAliasError("alias cannot be an integer")
        if type(alias) is not str:
            raise exceptions.InvalidAliasError("alias must be a string")
        if contains_special_chars(alias):
            raise exceptions.InvalidAliasError("alias cannot contain any special characters other than '_', '.', '-'")
        # validate that it doesn't match with temp_seq_id
        if Asset.is_temp_seq_id(alias):
            raise exceptions.InvalidAliasError(f"alias cannot start with: {Asset.TEMP_SEQ_PREFIX}")

    def add_files(self, targets: [str],
                  prompt_user: bool,
                  object_type: str = None,
                  mode: str = "add",
                  proxy: bool = False,
                  dest_dir: str = None,
                  ignore: str = None,
                  force: bool = False):
        """Adds a file or directory to assets.

        Parameters
        ----------
        targets : list of str
            List of files or directories to add.
        prompt_user : bool
            Whether to prompt the user for confirmation.
        object_type : str, optional
            Type of object to add.
        mode : str, optional
            Mode to prompt user, either 'add' or 'update' (default is "add").
        proxy : bool, optional
            Whether to use proxy (default is False).
        dest_dir : str, optional
            Destination directory to add files.
        ignore : str, optional
            Ignore pattern, takes glob.
        force : bool, optional
            Whether to force add files ignoring .assetignore patterns.

        Raises
        ------
        exceptions.AssetException
            If there is an error adding the files.
        exceptions.InvalidObjectSourceError
            If no valid sources are found to add.
        """
        if object_type and object_type not in ALLOWED_OBJECT_TYPES:
            e = exceptions.AssetException(msg=f"invalid option for type: {object_type}")
            e.logs.add(f"permitted values are: {','.join(ALLOWED_OBJECT_TYPES)}", LogColors.INFO)
            raise e

        self.raw_mode = bool(object_type)
        if self.asset.frozen:
            self.user_log.alert("asset is frozen, no more edits allowed")

        # check linking type
        if self.asset.repo.linking_type != "copy":
            raise exceptions.ReadOnlyAssetError(
                f"read-only asset, change tracking and updates are disabled: {self.asset.repo.linking_type}")

        pbar = None
        try:
            if proxy:
                # toggle to use content credentials, since there are proxy contents
                # note: this is one of the only two places we use content credentials
                # the other place is while downloading proxy assets
                StorageCredentials.shared().use_content_credentials = True

            sources: dict = self.get_object_sources(targets=targets,
                                                    proxy=proxy,
                                                    dest_dir=dest_dir,
                                                    ignore=ignore)
            if proxy:
                # toggle back to use project credentials
                StorageCredentials.shared().use_content_credentials = False

            if not sources:
                e = exceptions.AssetException(msg="nothing to add to the asset")
                e.logs.add("please check the paths added and try again", LogColors.INFO)
                raise e

            if len(sources) > 1:
                e = exceptions.AssetException(msg="multiple sources detected")
                e.logs.add("please add files from one source at a time", LogColors.INFO)
                raise e

            # filter out .assetignore patterns only if force is not set
            if not force:
                storage_name = next(iter(sources))  # we have only one key in sources
                # update the sources with .assetignore filtered sources
                sources[storage_name] = AssetIgnore(self.asset.repo_dir).filter_sources(sources=sources[storage_name],
                                                                                        asset=self.asset)

            count = self.ask_user(sources=sources, prompt_user=prompt_user)
            if not count:
                return

            pbar = Progress.progress_bar(total=count, desc="adding files")
            added, updates, ignored = self.asset.create_and_add_objects(data=sources,
                                                                        object_type=object_type,
                                                                        p_bar=pbar,
                                                                        proxy=proxy)
            if object_type and (added or updates):
                # we need to parse out members
                members_add, members_update = set(), set()
                for obj in added:
                    if isinstance(obj, GroupObject):
                        # get the members, so we can display to user
                        members_add = members_add.union(set(obj.load_members()))

                for obj in updates:
                    if isinstance(obj, GroupObject):
                        members_update = members_update.union(set(obj.load_members()))

                added = members_add or added
                updates = members_update or updates
            self.user_message(added=added, updates=updates, ignored=ignored, mode=mode)

        except exceptions.AssetException as e:
            if pbar:
                pbar.close("\n")
            # add invalid target paths to the error message
            if isinstance(e, exceptions.InvalidObjectSourceError):
                e.msg = f"target not found: {','.join(targets)}"
            e.logs.add("operation aborted", LogColors.ERROR)
            raise

    def ask_user(self, sources: dict, prompt_user: bool):
        count = functools.reduce(lambda x1, x2: x1 + len(x2), sources.values(), 0)
        if not count:
            raise exceptions.InvalidObjectSourceError()

        if not prompt_user:
            # no need to ask the user
            return count

        # ask for user feedback
        message = f"this will add {count} files to the asset, do you wish to continue?"
        user_input: str = self.user_log.ask_user(question=message, options=["y", "n"], default="y")
        if user_input and user_input.lower() == 'y':
            return count
        else:
            self.user_log.info("aborted")
            return 0

    def get_object_sources(self, targets: list,
                           proxy: bool = False,
                           dest_dir: str = None,
                           ignore: str = None) -> dict:
        """Collects source information for the given targets.

        Parameters
        ----------
        targets : list
            List of files or directories to add.
        proxy : bool, optional
            Whether to use proxy.
        dest_dir : str, optional
            if provides, the dest_dir is created and files are added there.
        ignore : str, optional
            Ignore pattern, takes glob.

        Returns
        -------
        dict
            Parsed sources information.

        Raises
        ------
        exceptions.AssetException
            If there is an error collecting source information.
        """
        pbar = Progress.status_bar(desc="collecting source information")
        try:
            parsed_sources = ObjectFactory().parse_sources(repo_dir=self.asset.repo_dir,
                                                           targets=targets,
                                                           proxy=proxy,
                                                           dest_dir=dest_dir,
                                                           ignore=ignore)
            pbar.close(message="done")
            return parsed_sources
        except exceptions.AssetException:
            pbar.close(message="error")
            raise

    def add_commit_message(self, message):
        self.asset.commit_message = message

    def user_message(self, added: list, updates: list, ignored: list, mode: str = "add"):
        if mode == "add":
            self.user_log.message(body=f"added {len(added)} new files to asset", color=LogColors.INFO)
        if added:
            self.user_log.message(body="list of added:")
            InfoAPI(asset=self.asset).print_objects_table(objects=added)
        if updates:
            self.user_log.message(
                body=f"updated {len(updates)} file{'s' if len(updates) > 1 else ''} in the asset, list of updates:",
                color=LogColors.INFO)
            # self.user_log.message(body=f"List of Updated Objects:")
            InfoAPI(asset=self.asset).print_objects_table(objects=updates)
        if ignored:
            self.user_log.message(
                body=f"found {len(ignored)} existing file{'s' if len(updates) > 1 else ''} "
                     f"in the asset, list of existing:",
                color=LogColors.INFO)
            # self.user_log.message(body=f"List of existing files:")
            InfoAPI(asset=self.asset).print_objects_table(objects=ignored)
