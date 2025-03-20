# v2.2.15

Enhancements and bug-fixes:

```shell
asset config set -k dashboard_url # set asset dashboard url
```

# v2.2.14

Python-API features:

```shell
artifact.set_attributes() # set the attributes of the asset
artifact.attributes # get the attributes of the asset
asset.store.clear(confirm=True) # clear the asset-store without user confirmation
artifact.set_alias() # set the alias of the asset
```

Enhancements and bug-fixes:

```shell
asset clone --proxy --cred # switch to the content credentials in transporter
asset store prune # fix non existing asset store issue
asset auth login # use updated google_oauth
asset info # added attributes
asset info --attributes # print attributes of the asset
asset list --class # list all assets of that class
asset list --class --locations # list all assets with their locations
asset store clear --yes # clear the asset-store without user confirmation
asset alias set # set the alias of the asset
```

Internal & maintenance:

```shell
integration-test # update the proxy files and assets
integration-test # cleanup the directory and move tests to utilities
assets_backup # skip creating backup and remove related code
exceptions.NestedRepoError # check if asset name is unavailable
asset-plugin-s3 # remove Roche specific test data
ci.yml # inject the Roche specific URLs during asset-core build
asset-core # remove all Roche specific URLs from config
ConfigModes.DEV # use DEV as default config mode
asset-core # update the server_config routes
asset-core # add bearer_token and remove user_id from server api calls
asset-core # update dependencies
asset-plugin-s3 # add asset-sever functionalities and update dependencies
asset-plugin-gcs # add asset-sever functionalities and update dependencies
asset-plugin-posix # add asset-sever functionalities and update dependencies
```

# v2.2.13

Python-API features:

```shell
artifact.set_title() # set the title of the artifact
artifact.set_description() # set the description of the artifact
artifact.add_tags() # add tags to the artifact
artifact.remove_tags() # remove tags from the artifact
artifact.set_metadata() # set the metadata of the artifact
artifact.title # get the title of the artifact
artifact.description # get the description of the artifact
artifact.tags # get the tags of the artifact
artifact.metadata # get the metadata of the artifact
artifact.set_alias() # deprecating artifact.add_alias()
artifact.info # added title, description, tags and metadata
asset.disable_logging() # disable printing logs
asset.clone(exists_ok=True) # check alias name too for existing asset
artifact.info # update the dictionary without converting to string
artifact.remove_alias() # remove alias from the artifact
```

Enhancements and bug-fixes:

```shell
asset alias set # deprecating asset alias add
asset info # added title, description, tags and metadata fields
asset info --metadata # print metadata of the asset
asset store set # fix bugs while moving or deleting asset-store
asset find # ask user for server access instead of printing warning
asset alias remove # remove alias from the asset
```

Internal & maintenance:

```shell
asset-utils # add asset-sever functionalities and update dependencies
asset-pluggy # add asset-sever functionalities and update dependencies
```

# v2.2.12

Enhancements and bug-fixes:

```shell
asset fetch --versions # download 50 versions of the asset
asset history # display 10 versions in descending order
asset versions # display 10 versions in descending order
asset union # fix the w.r.t. version in the text file
asset upload # check and update status of the asset before upload
asset clone # check status of the asset before cloning
```

Internal & maintenance:

```shell
asset manifest # use snapshots to optimize manifest file creation
asset clone # # create and use snapshots to optimize cloning
asset upload # create and use snapshots to optimize uploading
asset switch # use objects snapshots to optimize switching versions
AssetSnapshot # new class to manage snapshots of the version objects
cli_version # get version in asset-core using importlib.metadata
Warning check # parse and print Warning messages from the server response
repo.json and file_stats.json # revert back to json for backward compatibility
google_oauth_v2 # auth_server use auth url instead of configs
Configs clean up # remove all config yaml files and update all config classes
StatusEnums # new status and checks for download and upload
class owner # new field added to asset class
class status # new field added to asset class
asset status # new field added to asset
```

# v2.2.11

Enhancements and bug-fixes:

```shell
artifact.file_url() # get the dashboard url of the file in the asset
linking_type # warn user if linking type is not copy
asset info # print the files in a sorted order
asset config num_retries # set the number of retries for downloads
```

Internal & maintenance:

```shell
linking_type # store linking type in the repo.json
asset-core # fix unit tests
asset-core # cleanup and reformat code
asset-plugin-s3 # clean up internal data and reformat code
asset-plugin-s3 # get pytest coverage above 70%
aggregated retry # retry gcs downloads in groups
on_transfer_complete() # check if the file is downloaded
IncorrectServerResponseError # raise error if the server response is incorrect
asset_fetcher # check if the class file is downloaded
```

# v2.2.10

Python-API features:

```shell
asset.copy(src, dst) # expose the asset cp command
asset.config.set(key, value) # use any type for the value instead of just string
artifact.alias_name # get the asset name with alias
artifact.alias_version_name # get the asset version name with alias
```

Enhancements:

```shell
asset init # print useful urls after successful initialization
asset info --alias_name # get the asset version name with alias
```

Internal & maintenance:

```shell
gcs_client.list_blobs() # revert back to storage_utils.filter_blobs()
config environ # update all the asset-manager env variables with ASSET_ prefix
asset-manager # reformat and fix flake8 issues
hello world doc # create a hello world doc for asset-manager
pip ci # update the ci.yml for pip
config batch_size # set default batch size to 16
asset-core # reformat and fix flake8 issues
Quick Start Guide # updated the quick start mkdocs
asset-contents # clean up internal data and reformat code
asset-contents # get pytest coverage above 70%
python_api docs # update the mkdocs for github pages
```

# v2.2.9

Enhancements and bug-fixes:

```shell
asset find # need to set server_access to access the asset-server
asset config server_access # access to the asset-server, default is False
operate from a mounted bucket # support aws s3 bucket
asset config bucket_mt_config # set bucket mount config
asset config server_url # set asset server url
```

Internal & maintenance:

```shell
gcs_client.list_blobs() # filter pattern directly with match_glob
asset-plugin-posix # clean up internal data and reformat code
asset-plugin-posix # get pytest coverage above 70%
asset-plugin-gcr # clean up internal data and dependencies
asset-plugin-gcr # get pytest coverage above 70%
asset-plugin-s3 # added support for mounted buckets
asset-pluggy # added support for mounted buckets MountConfig
```

# v2.2.8

Enhancements and bug-fixes:

```shell
asset add --proxy # enable adding s3 files as proxy
.assetignore # filter files from proxy/remote sources
asset store clear  # default behavior to be 'y'
```

Internal & maintenance:

```shell
asset-plugin-gcs # clean up internal data and reformat code
asset-plugin-gcs # get pytest coverage above 70%
try-catch block for the OSLink error for .asset backup
```

# v2.2.7

Python-API features:

```shell
asset.store.set() # set the asset store
asset.store.clear() # clear the asset store
asset.store.info() # get the asset store information
asset.store.prune() # prune the asset store
asset.config.set() # set the key value pair in asset config
asset.config.reset() # reset the keys in asset config
asset.config.info() # get the asset config information
```

Enhancements and bug-fixes:

```shell
asset init # check for nested repo while initializing
asset clone # check for nested repo while cloning
copy an asset repo # allow multiple copies of a repo
move an accet repo # allow moving a repo to a different location
```

Internal & maintenance:

```shell
Repo() # check for nested repo while initializing the repo
Repo() # update store.json while initializing the repo
repo metadata # change meta_dir from .assets to .asset inside the repo
skip restore_from_backup() # still creating the backup, but won't restore from it
asset-db # clean up and reformat code
asset-db # bring pytest coverage above 70%
```

# v2.2.6

Python-API features:

```shell
artifact.pull() # pulls the artifact to the latest version
asset.clone_or_pull() # clones or pulls the existing asset to the latest version
asset.clone(soft=True) # clones the asset without downloading the files
asset.clone(credentials) # clones the asset with user provided credentials
artifact.add(force=True) # force add ignored files from .assetignore
artifact.add(copy_to_asset=True) # copy files outside of the asset Repo before adding
```

Enhancements:

```shell
asset pull # pulls the asset to the latest version
asset status # list changes in a git status like format
.assetignore # ignore files and directories similar to .gitignore
asset add --force # force add ignored files from .assetignore
asset add --ignore # deprecated, use .assetignore instead
asset cp # can handle urls with just the bucket name
```

Internal & maintenance:

```shell
asset-utils # update dependencies
asset-contents # update dependencies
```

# v2.2.5

Enhancements:

```shell
asset find --size # fetch size of the latest version if version is not provided
asset.find_size() # fetch size of the latest version if version is not provided
```

# v2.2.4

Python-API features:

```shell
artifact.alias # get the alias of the artifact
artifact.add_alias() # add alias to the artifact
artifact.add_remote() # add gcs urls to the artifact
```

Internal & maintenance:

```shell
asset-pluggy # clean up and reformat code
asset-pluggy # bring pytest coverage above 70%
utilities/test_asset_python_api.py # integration tests for python api in ci
```

# v2.2.3

Python-API features:

```shell
updated the python api documentation
asset store # set up asset store while using python api
```

Bug-fixes & enhancements:

```shell
asset clone # fetch class list from remote
asset find # cleaner class fetching
api.environment() # bug-fix for nested environment throwing exceptions
content credentials # add content_credentials to store user provided credentials
asset add --proxy --cred # bug-fix adding proxy files with user provided credentials
asset clone --cred # bug-fix for downloading proxy files with user provided credentials
```

Internal & maintenance:

```shell
asset-utils # clean up and reformat code
asset-utils # bring pytest coverage above 70%
```

# v2.2.2

New Python-API features:

```shell
ArtifactRef # a proxy artifact to use remote functions
artifact_ref.size # get the size of the artifact from remote
artifact_ref.inputs.add() # add inputs to the artifact remotely
artifact_ref.inputs.list() # get inputs of the artifact from remote
asset.get_or_init() # get or initialize an asset
artifact.class_name # get the class name of the artifact
artifact.hash # get the objects hash of the artifact
artifact.is_temp # check if the artifact is temporary/not uploaded
artifact.find_duplicates() # find all the duplicates of an artifact
artifact.find_latest_duplicate() # find the latest duplicate of an artifact
asset.fetch() # fetch asset or class from remote
artifact.fetch() # fetch all the versions of an artifact from remote
asset.exists() # check if the asset exists
artifact.exists() # check if the asset exists
artifact_ref.exists() # check if the asset exists
asset.get_or_init() # get or initialize an asset
WandB plugin # add plugin for Weights and Biases
```

Bug-fixes & enhancements:

```shell
asset info # add hash to the asset info
resolve dependencies # resolve conflicts with acap
asset alias add # allow period(.) in asset alias
save and restore env variables # add support for nested api.environment()
asset find --alias # fetch alias from bucket
asset server bug # set ConfigModes for python api
```

# v2.2.1

New Python-API features:

```shell
artifact.size # get size of an artifact
artifact.switch_version() # switch version of an artifact
asset.clone() # return existing artifact instead of cloning
asset.find_size() # query asset version size from server
```

Bug-fixes & enhancements:

```shell
asset info # add current version size
asset versions # add size column
version size # add size field to version.yaml
asset find --size # query asset version size from server
asset auth login # reuse existing user login
asset alias add # allow dash in asset alias
```

- Setting `ASSET_SERVER_SKIP_DNS=true` now lets `asset auth` module to use IP.

# v2.2.0

Python 3.8, 3.9 and 3.10 Support.

# v2.1.4

New Python-API features:

```shell
asset.auth.login() # login to asset-manager
asset.auth.info() # get user information
asset.auth.logout() # logout from asset-manager
asset.auth.update() # update user login
asset.project.list() # list all projects
asset.project.activate() # activate a project
asset.project.active # get active project
asset.klass.fetch() # fetch all classes of a project
asset.klass.list() # list all classes of a project
asset.klass.info() # get information of a class
artifact.inputs # streamline the inputs functions
```

Bug-fixes & enhancements:

```shell
Python API mkdocs # updated asset-manager GutHub pages of python API
asset inputs add --remote # prompt user if asset version is not root
asset inputs add # bug-fix for adding existing inputs
asset inputs remove # remove inputs from an asset
asset status # list untracked files in the asset
ama # add new alias for asset
asset info # add current asset version
asset upload # print the updated asset version after upload
```

# v2.1.3

New Python-API features:

```shell
asset.clone() # clone an asset
asset.get() # use an existing asset
asset.init() # add_files flag to include files during asset creation
artifact.can_upload() # check if an artifact can be uploaded
artifact.inputs # support inputs of an artifact
artifact.inputs.add() # add inputs to an artifact locally
artifact.inputs.list() # list inputs of an artifact
ArtifactInputs.remote_add() # add inputs remotely
ArtifactInputs.remote_list() # list remote inputs of an artifact
```

Bug-fixes & enhancements:

```shell
asset-plugin-s3 # use AwsAuth for signing requests
python api # fix clone, create and _clear_cache methods
asset refs add # bug-fix for adding references while uploading
asset refs info # added --remote flag to list remote refs
asset inputs # changed asset refs to asset inputs
asset inputs info # updated the output format to list inputs instead of src and dst
asset inputs add # updated the command to add inputs to an asset
asset user_commands # updated the user commands to use asset inputs instead of asset refs 
asset inputs add --remote # prevent adding inputs to self
```

Maintenance:

```shell
cleanup_python_develop.py # update the script to work without setup.py
```

# v2.1.2

New features:

```shell
asset cp # copy, upload, and download file or directory
```

Bug-fixes & enhancements:

```shell
asset cp # preserve ETags while remote copying using multipart size
asset clone --remote # fix asset file paths during filtering
asset init # warn user if creating asset in home directory
asset list --class # bug-fix for missing class yaml file
aws blob initialize error # bug-fix for missing blob url
aws hash refactor # move aws hash calculations to asset-utils
aws hash update # support ETag calculation based on part size
python api # fix asset initialization
```

# v2.1.1

New features:

```shell
asset config set -k batch_size -v <unit> # set batch size for asset upload/download/copy
```

Bug-fixes & enhancements:

```shell
asset clone # calculate the hash during download to speed up checksum validation
asset checksum crc32c # new checksum validation support added
asset repo and store error # bug-fix by exceptions handling
asset-pugin-s3 cleanup # use single client for all operations
```

CICD maintenance:

- remove spaces from around specifier in asset-pluggy pyproject.toml

# v2.1.0

Bug-fixes & enhancements:

```shell
asset clone # added timer to all the progress bars
asset config set -k linking_type -v <type> # set asset linking type to either 'copy', 'hardlink' or 'symlink'
asset store set <store-location> # can now reuse any exixting asset-store
asset-manager python api # new python api for asset-manager
asset store set # bug fix
asset switch -v <version> # bug fix
asset alias add # check special characters in alias name
progress bar # prints out in stdout instead of stderr
asset class info # bug fix for different project
asset fetch # bug fix for outside of repo calls
```

pbar fix for `asset clone`:
error:

```
  File "/.../python3.8/site-packages/asset_core/asset/fetchers/fetcher.py", line 72, in perform_download
    pbar2.update(1)
AttributeError: 'NoneType' object has no attribute 'update'
```

# v2.0.11

New features:

```shell
asset clone --remote  # capability to clone an asset to a gcs or s3 bucket
asset report  # generate a html report using a default or provided jinja template
```

# v2.0.9

Bug-fixes & enhancements:

```shell
asset list  #  log improvement
asset  # log improvement
asset class list  # log improvement
asset -h  # log improvement
```
