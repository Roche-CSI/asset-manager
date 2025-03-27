import contextlib
import functools
import json
import os
import shutil

from asset_core.configs import Configs
from asset_core.configs.app_settings import AppSettings, UserSettings
from asset_core.server import AuthServer
from asset_core.server import base_server
from asset_core.store.asset_store import AssetStore
from asset_utils.common import user_commands, exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin, colored_string, LogColors
from asset_utils.utils.web_utils import open_in_browser


class SettingsAPI(LoggingMixin):

    @functools.cached_property
    def settings(self):
        return AppSettings.shared()

    @contextlib.contextmanager
    def user_settings(self):
        try:
            self.settings.user_configs.activate()
            yield
        except Exception:
            raise
        finally:
            self.settings.user_configs.deactivate()

    def open_asset_dashboard(self):
        with self.user_settings():
            url = Configs.shared().asset_home.dashboard_url
            if not url:
                raise exceptions.AssetException("asset dashboard url is not set")
            token = (self.settings.user or {}).get("token")
            if token:
                url = base_server.BaseServer().add_params(url=url, params={"token": token})
            self.user_log.message("opening asset dashboard in the browser")
            open_in_browser(url=url)

    def auth_update(self, jsonize=False):
        with self.user_settings():
            try:
                token = (self.settings.user or {}).get("token")
                if not token:
                    raise exceptions.InvalidCredentialError()
                return self.user_login(token=token, jsonize=jsonize)
            except exceptions.AssetException as e:
                e.logs.add(e.msg, LogColors.ERROR)
                e.msg = "cannot update asset authentications"
                raise

    def user_logout(self):
        # remove auth, user and projects
        self.settings.clear_user_data()
        self.user_log.info("logged out from asset-manager")

    def user_login(self, token=None, jsonize=False):
        """Attempts to log in a user either with a token or through email authentication.

        If a token is provided, it attempts to log in with the token. If no token is provided,
        it proceeds with email authentication. If the user is already logged in with the same token,
        it returns the current authentication status without re-authenticating.

        Parameters
        ----------
        token : str, optional
            The authentication token for the user. If not provided, email authentication is used.
        jsonize : bool, optional
            If True, the output will be in JSON format. Defaults to False.

        Returns
        -------
        dict or None
            Returns user authentication information if login is successful.

        Raises
        ------
        exceptions.ServerNotAvailableError
            If the asset-server is unreachable, possibly due to network issues or the server being down.

        Notes
        -----
        - If logging in with a token and the token matches the currently logged-in user's token,
          no new login attempt is made.
        - If logging without a token, and there is an existing user, no new login attempt is made.
        """
        with self.user_settings():
            existing_user = self.settings.user
            if existing_user:
                if not token or token == existing_user.get("token"):
                    self.user_log.info("you are already logged in, logout first to login as a different user")
                    return self.print_auth(jsonize=jsonize)
            try:
                if token:
                    return self._login_with_token(token=token, jsonize=jsonize)
                return self._login_with_email(jsonize=jsonize)
            except exceptions.ServerNotAvailableError as e:
                e.logs.add("unable to reach asset-server, are you connected to vpn?", e.log_colors.ERROR)
                raise

    def _login_with_email(self, jsonize=False):
        return self.save_user(res=AuthServer().google_oauth(), jsonize=jsonize)

    def _login_with_token(self, token: str, jsonize=False):
        return self.save_user(res=AuthServer().login_with_token(token=token), jsonize=jsonize)

    def user_signup(self, username: str, email: str):
        with self.user_settings():
            if not username or not email:
                raise exceptions.AssetException(msg="both username and email are required")
            if not self.valid_email(email=email):
                raise exceptions.AssetException(msg="invalid email, you can only signup with a valid email")

            self.user_log.info("signing into asset-manager...")
            res = AuthServer().signup_user(username=username, email=email)
            if res.get("id") and res.get("username"):
                self.user_log.message("user already exists, logging in...")
                self.user_login()

    def print_user_configs(self, show_help=True, jsonize=False):
        user_cfgs = self.settings.shared().user_configs
        cfg_data: dict = user_cfgs.printable_format()
        if jsonize:
            return cfg_data

        columns = {"key": "Key", "value": "Value", "default": "Default", "type": "Type", "description": "Description"}
        rows = [
            {
                "key": key,
                "value": cfg_data[key]["value"],
                "default": cfg_data[key]["default"],
                "type": cfg_data[key]["type"],
                "description": getattr(user_cfgs, key).help
            } for key in cfg_data
        ]
        self.user_log.table(columns=columns, rows=rows, table_fmt="simple")

        if show_help:
            self.user_log.message(user_commands.UserCommands().set_user_configs())
            self.user_log.message(user_commands.UserCommands().reset_user_configs())

    def set_user_configs(self, kwargs: dict):
        if not kwargs:
            e = exceptions.AssetException(msg="missing config options, you must pass the option you want to set")
            e.logs.add(user_commands.UserCommands().set_user_configs())
            raise e

        # if the user tries to set server_url, make sure they are not logged in
        # as we don't use token in server, we need to make sure user logs in after setting the server_url
        # TODO: remove this after we have token based auth for server
        if "server_url" in kwargs and self.settings.user:
            raise exceptions.AssetException(msg="cannot set the 'server_url' while logged in, please logout first")

        try:
            cfg: UserSettings = self.settings.shared().user_configs
            cfg.update(kwargs)
            cfg.save()
        except exceptions.AssetException:
            raise

        self.user_log.success(f"success: updated user-configs with {json.dumps(kwargs)}")
        self.print_user_configs(show_help=False)
        self.user_log.message(user_commands.UserCommands().reset_user_configs())

    def reset_user_configs(self, keys: [str]):
        if not keys:
            e = exceptions.AssetException(msg="missing config keys, you must pass the key you want to reset")
            e.logs.add(user_commands.UserCommands().reset_user_configs())
            raise e

        user_cfgs: UserSettings = self.settings.shared().user_configs
        for key in keys:
            try:
                user_cfgs.reset(key=key)
            except exceptions.AssetException as e:
                e.logs.add(user_commands.UserCommands().configs_info())
                e.logs.add(user_commands.UserCommands().set_user_configs())
                raise

        user_cfgs.save()
        self.user_log.success("success: reset user-configs: {}".format(", ".join(keys)))
        self.print_user_configs(show_help=False)

    def valid_email(self, email: str):
        if "mydomain.com" not in email:
            return False
        return True

    def save_user(self, res: dict, jsonize=False):
        user = res.get("user") if res else None
        if user and user.get("id"):
            # save to settings
            self.settings.default_project = res.get("default_project", None)
            self.settings.user = res.get("user")
            self.settings.set_roles(res.get("roles"), append=False)

            # print success message
            message = colored_string("Success\n", LogColors.SUCCESS)
            message += colored_string("Signed in as: {}".format(colored_string(res.get("user").get("username"),
                                                                               LogColors.INFO)))
            self.user_log.message(message)
            if self.settings.active_project:
                projects = self.print_all_projects(jsonize=jsonize)
                if jsonize:
                    for project in projects:
                        project['active'] = bool(self.settings.active_project == project["id"])
                        project.pop("id")  # remove id, user shouldn't need it
                    return {
                        "username": user.get("username"),
                        "email": user.get("email"),
                        "token": user.get("token"),
                        "projects": projects
                    }
            else:
                e = exceptions.InvalidCredentialError(msg="invalid credentials")
                e.logs.add("You don't have access to a project yet", LogColors.ERROR)
                e.logs.add("To create a new project or get access: <ASSET_DASHBOARD_URL>",
                           LogColors.INFO)
                raise e
        else:
            error: dict = res.get('error')
            error = error.get('value') if type(error) is dict else error
            e = exceptions.InvalidCredentialError(msg=error)
            e.logs.add(user_commands.UserCommands().user_login())
            e.logs.add(user_commands.UserCommands().user_signup())
            raise e

    def print_auth(self, jsonize=False):
        settings = self.settings
        if not settings.user:
            e = exceptions.InvalidCredentialError("invalid user")
            e.logs.add("user not logged in", LogColors.ERROR)
            e.logs.add(UserCommands().user_login())
            raise e

        columns = {
            "section": "",
            "details": "",
        }
        project = settings.projects.get(settings.active_project, {})

        data = {
            "username": settings.user.get("username"),
            "email": settings.user.get("email"),
            "project": project.get("name", "not set")
        }
        if jsonize:
            return data

        rows = [{"section": f"{key}", "details": f"{data[key]}"} for key in data]

        self.user_log.table(columns=columns, rows=rows, table_fmt="plain")
        self.user_log.message(UserCommands().user_token())
        self.user_log.message(UserCommands().list_projects())

    def print_auth_token(self, jsonize=False):
        """Prints the user auth token
        Parameters
        ----------
        jsonize: If true returns the json formatted output

        Returns
        -------

        """
        settings = self.settings
        if not settings.user:
            e = exceptions.AssetException(msg="missing user")
            e.logs.add(color=LogColors.ERROR, message="user not logged in")
            e.logs.add(color=None, message=UserCommands().user_login())
            raise e

        result = {"token": settings.user.get('token')}
        if jsonize:
            return result
        else:
            self.user_log.message(self.user_log.dict_to_logs(result))

    def asset_home_info(self, jsonize=False):
        if self.settings.assets_home:
            result = {"asset-store": self.settings.assets_home}
            if jsonize:
                return result
            self.user_log.message(self.user_log.dict_to_logs(result), color=LogColors.INFO)
        else:
            e = exceptions.AssetStoreInvalidError("asset-store is not set yet")
            e.logs.add(UserCommands().set_asset_store())
            raise e

    def prune_asset_store(self):
        """Removes all invalid assets from the asset-store."""
        if self.settings.assets_home:
            try:
                if AssetStore.shared().prune_repos():
                    self.user_log.success("Removed invalid assets from the asset-store")
                else:
                    self.user_log.info("No invalid assets found, asset-store is clean")
            except exceptions.AssetStoreInvalidError as e:
                e.msg = "asset-store is not set yet"
                e.logs.add(UserCommands().set_asset_store())
                raise
            except Exception as e:
                raise exceptions.AssetException(f"error pruning asset store: {e}")

    def set_asset_home(self, dst_dir):
        # use realpath to resolve symlinks
        # check if this is same as existing, if yes - do nothing
        dst_dir = os.path.realpath(os.path.abspath(dst_dir))
        if not os.path.exists(dst_dir):
            proceed = self.user_log.ask_user(question=f"{dst_dir} does not exist, do you want to create it?",
                                             options=["y", "n"], default="y")
            if proceed.lower() == "n":
                return

        # REUSE EXISTING STORE
        # if there is already a valid store at dst_dir
        # we just update the globals.json to point to the dst_dir
        if AssetStore.is_store_exists(dst_dir):
            # we reuse this store and no need to do anything else
            self.settings.assets_home = dst_dir  # this will update the globals.json
            self.user_log.success(f"success: reused existing asset store at: {dst_dir}")
            return

        # CHECK IF WE CAN CREATE A NEW STORE IN THE DST_DIR
        AssetStore.validate_store_dir(AssetStore.get_store_dir(dst_dir))

        # CREATE NEW ASSET STORE
        self.user_log.message(f"creating a new asset-store at: {dst_dir}")
        existing_store = self.store_exists()
        if existing_store:
            # if there is an existing store, ask user should we move the store to the new location or
            # delete the old one and create a fresh one
            msg = f"found an existing store at: {existing_store.home_dir}, please choose:\n"
            msg += "1. move the existing store and its contents to the new location\n"
            msg += "2. delete the existing store and create a new one at the new location\n"
            msg += "3. keep the existing store and create a new one at the new location"
            self.user_log.message(msg)
            user_input = self.user_log.ask_user(question="please select an option.",
                                                options=["1", "2", "3"],
                                                default="1")
            if user_input == "1":
                # move store and its contents to new location
                FileUtils.move(src=existing_store.store_dir, dst=dst_dir)
                self.settings.assets_home = dst_dir
            elif user_input == "2":
                # create new and then delete the old one
                existing_store_dir = existing_store.store_dir
                self.settings.assets_home = dst_dir
                AssetStore.create_store()
                # delete existing
                shutil.rmtree(existing_store_dir)
            elif user_input == "3":
                self.settings.assets_home = dst_dir
                AssetStore.create_store()
            else:
                raise exceptions.AssetStoreCreateError("invalid option for setting asset-store")
        else:
            # no existing store, create a new one
            self.settings.assets_home = dst_dir
            AssetStore.create_store()

        self.user_log.success("Success")
        self.user_log.info(f"asset-store is now set to: {dst_dir}")

    def store_exists(self):
        if self.settings.assets_home:
            try:
                return AssetStore.shared()
            except exceptions.AssetStoreInvalidError:
                return None

    def remove_asset_home(self, confirm=False):
        """Removes the asset-store and clears all its contents"""
        if self.settings.assets_home:
            try:
                target = AssetStore.shared().store_dir
                if not confirm:
                    # config dont_ask_user won't work here, so we need to rely on confirm flag
                    proceed = self.user_log.ask_user(
                        question="this will remove all assets and its contents, do you want to continue?",
                        options=["y", "n"], default="y"
                    )
                    if proceed.lower() != "y":
                        return
                if os.path.exists(target):
                    shutil.rmtree(path=target)
            except exceptions.AssetStoreInvalidError as e:
                e.msg = "asset-store is not set yet"
                e.logs.add(UserCommands().set_asset_store())
                raise
            except Exception as e:
                raise exceptions.AssetException(f"error removing asset store: {e}")

            self.user_log.success("Success")
            self.user_log.info(f"removed asset-store and all its contents from: {self.settings.assets_home}")

    def set_active_project(self, project_name: str):
        for project in self.settings.projects.values():
            if project.get("name") == project_name:
                self.settings.active_project = project.get("id")
                self.user_log.success("Success")
                self.user_log.info(f"active project: {project_name}")
                self.print_all_projects(show_help=False)
                return True
        raise exceptions.AssetException(f"project: {project_name} not found")

    def print_project_list_table(self, projects=[], jsonize=False):
        if not self.settings.projects:
            message = colored_string("there are no projects", LogColors.INFO)
            message += "please login to the asset-manager to see the projects you have access to\n"
            message += UserCommands().user_login()
            self.user_log.message(message)
            return None

        columns = {
            "index": "#",
            "name": "Project Name",
            "id": "ID",
            "remote_url": "Remote-URL",
        }
        # switch 'is_active': it has different meanings for server and client
        for project in projects:
            project["is_active"] = bool(project["id"] == self.settings.active_project)

        data = [self.formatted_project(idx=idx, project=project) for idx, project in enumerate(projects)]
        if jsonize:
            return [
                {
                    key: project[key] for key in ["name", "id", "remote_url", "is_active", "description"]
                } for project in projects
            ]

        self.user_log.table(columns=columns, rows=data)

    def print_all_projects(self, show_help=True, jsonize=False):
        projects = self.print_project_list_table(projects=list(self.settings.projects.values()), jsonize=jsonize)
        if show_help:
            self.user_log.message(UserCommands().activate_project())
        if jsonize:
            return projects

    def print_active_project(self, jsonize=False):
        if not self.settings.active_project:
            raise exceptions.NoActiveProjectError()

        active_project_info = self.settings.projects.get(self.settings.active_project)
        if jsonize:
            return {key: active_project_info[key]
                    for key in ["name", "id", "description", "remote_url", "is_active"]}

        self.print_project_list_table([active_project_info])
        self.user_log.message(UserCommands().list_projects())

    def formatted_project(self, idx: int, project: dict):
        keys = ["name", "id", "remote_url"]
        readable = {
            "index": f"{idx}",
            **{key: project[key] for key in keys}
        }
        if project["is_active"]:
            readable["index"] = f"{readable['index']} active"
            for each_field in readable:
                readable[each_field] = colored_string(readable[each_field], color=LogColors.ACTIVE)

        return readable
