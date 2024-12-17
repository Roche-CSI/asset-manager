# Asset SDK for Python

A Python library for the Asset-Manager. It lets you do anything the asset cli does, but from within Python apps – create
assets,
clone assets, access files, upload, find assets etc.

This assumes that you have already installed and configured asset-manager, please refer the `User Guide` section on how
to install `asset-manager`.

#### How to authenticate asset-manager for use

```python
from asset_manager import asset

# to login with Google account
# this will open a browser window to authenticate with Google
asset.auth.login()

# to login with an asset token
# token is the token obtained from asset-manager
asset.auth.login(token=token)

# to get the auth information
# this will return a dictionary with the auth information
auth_info = asset.auth.info()

# to get the auth token along with the auth information
auth_info = asset.auth.info(token=True)
token = auth_info.get("token")

# to logout from asset-manager
asset.auth.logout()
```

#### How to manage Projects

```python
from asset_manager import asset

# to list all the projects available to the user
projects = asset.project.list()

# to activate a project
# project_name is the name of the project to be activated
asset.project.activate(project_name=project_name)

# to get the active project
active_project = asset.project.active
```

#### How to manage asset Classes

```python
from asset_manager import asset

# to fetch information about all the asset classes of the active project
asset.klass.fetch()

# to list info of all the asset classes of the active project
classes = asset.klass.list()

# to get the info of a specific class_name
class_info = asset.klass.info(class_name=class_name)
```

#### How to clone an asset

```python
# clone the asset at the target location
# asset_name is <class-name>/<seq-id> or <class-name>/<seq-id>/<version>
# path is your local target location where you want the asset to be cloned
# unlike the asset command line, this will not create a dir with <class-name>/<seq-id>
# if you want to use <class-name>/<seq-id> dir, you have to add it to the target_location

from asset_manager import asset, Artifact

# use <class-name>/<seq-id> to clone the latest version of the asset
artifact: Artifact = asset.clone(name=asset_name, path=location)

# use <class-name>/<seq-id>/<version> to clone a specific version of the asset
artifact: Artifact = asset.clone(name=asset_version_name, path=location)

# to clone just the metadata of the asset (soft clone)
# this will not download the files of the asset
artifact: Artifact = asset.clone(name=asset_name, path=location, soft=True)

# use exists_ok=True to clone the asset even if the asset already exists
# if you provide a different version, it will switch to the specified version
artifact: Artifact = asset.clone(name=asset_version_name, path=location, exists_ok=True)

# to clone or pull the existing asset to the latest version
# this will clone the asset if it does not exist
# if the asset exists, it will pull the latest version of the asset
artifact: Artifact = asset.clone_or_pull(name=asset_name, path=location)

# use force=True to avoid asking for user confirmation
artifact: Artifact = asset.clone_or_pull(name=asset_name, path=location, force=True)

# if you have remote/proxy files that are not accessible by the project credentials
# give the path to the credentials file to access the remote files
artifact: Artifact = asset.clone(name=asset_version_name, path=location, credentials="path/to/credentials.json")
```

#### How to use an asset

```python
from asset_manager import asset, Artifact

# this assumes that asset is available locally
# local_path is your local path where asset is available
artifact: Artifact = asset.get(local_path)
```

#### How to initialize an asset

```python
from asset_manager import asset, Artifact

# to initialize an asset for class_name at local_path
artifact: Artifact = asset.init(class_name=class_name, path=local_path)

# if you want to re use the existing asset, you can use get_or_init
# this will initialize the asset if it is not already initialized
# if the asset is already initialized, it will return the existing artifact
artifact: Artifact = asset.get_or_init(class_name=class_name, path=local_path)
```

#### How to add files to an asset

```python
# to add files to the asset use a file_path list
# file_path can be relative to the asset path if it is inside the asset directory
artifact.add([file_path_1, file_path_2, ...])

# by default, files being added should be inside the asset directory path
# to add files that are not inside the asset directory use copy_to_asset=True
# this will copy the files to the asset directory first and then add them
artifact.add([file_path_1, file_path_2, ...], copy_to_asset=True)

# you can have a .assetignore file in the asset directory to ignore adding files
# .assetignore uses the same patterns as .gitignore
# add files ignoring the .assetignore file using force=True
artifact.add([file_path_1, file_path_2, ...], force=True)

# to add all the files in the local_path while initializing the asset use add_all=True
# this will add all the files in the asset directory to the asset
artifact: Artifact = asset.init(class_name=class_name, path=local_path, add_files=True)

# to add remote files to an asset use add_remote()
# this will add file or directory from a gs or s3 bucket to the asset
artifact.add_remote(targets=["gs://bucket-name/file-path.txt"])

# to add all files in a remote directory use the directory url
# this will add all the files maintaining the directory structure
artifact.add_remote(targets=["gs://bucket-name/dir-path"])

# to add remote files not accessible by the project credentials use credentials
# give the path to the credentials file to access the remote files
artifact.add_remote(targets=["gs://bucket-name/dir-path"], credentials="path/to/credentials.json")
```

#### How to update contents of an asset

```python
# after altering any files in an asset you can update the asset
# need to do this before uploading
artifact.update()
```

#### How to upload an asset

```python
# check if the asset is ready to be uploaded can_upload()
artifact.can_upload()

# upload the asset to cloud with a commit message
artifact.upload(commit_message)
```

#### How to get information of an asset

```python
# to get the asset name from the artifact
# returns a string such as <class-name>/<seq-id>
asset_name: str = artifact.asset_name

# to get the class name from the artifact
# returns a string such as <class-name>
class_name: str = artifact.class_name

# to get the asset name with version from the artifact
# returns a string such as <class-name>/<seq-id>/<version>
asset_version_name: str = artifact.asset_version_name

# to get the active version of asset
# returns a string such as 0.0.0 or 0.1.1 etc.
active_version: str = artifact.active_version

# to obtain information about the asset
# returns a dictionary: {"asset": {}, "objects": []}
# "asset": has all the information about the asset
# "objects": has information about all the files in the asset

# "objects" dictionary: [{ cloned: bool, linked_path: str, path: str, size: int }]
info: dict = artifact.info

# gives information on all the different versions of the asset
# returns a dictionary: {}
versions: dict = artifact.versions

# gives information on history of the asset
history: dict = artifact.history

# to get the size of the asset
size: int = artifact.size

# to get the object hash of the asset
hash: str = artifact.hash
```

#### How to update or switch the version of an asset

```python
# to pull the latest version of an existing asset
artifact.pull()

# use force=True to avoid asking for user confirmation
artifact.pull(force=True)

# to switch to a specific version of the asset use switch()
# version number must be a string such as 0.0.0 or 0.1.1 etc.
artifact.switch_version(version_number)
```

#### How to access the files in an asset

```python
from asset_manager import asset, Artifact

# get asset
artifact: Artifact = asset.get(local_path)

# files is a dictionary {path: File}
for file in artifact.files.values():
    # similar to open(filepath), you can also do open(file)
    with file.open() as f:
        # do something here
        print(f.read())

# to access a specific file
# file_path is the relative path of file inside the asset
# this way you don't have to remember the actual location of the asset
file = artifact.files.get(file_path)
with file.open() as f:
    # do something here
    print(f.read())
```

#### How to fetch metadata of an asset or asset-class

```python
from asset_manager import asset

# this will fetch information about the asset, files are lazy downloaded and only
# gets downloaded when you switch to a different version

# to fetch all the version metadata of an asset
asset.fetch(asset_name=asset_name)

# to fetch all the asset metadata of an asset-class
asset.fetch(class_name=class_name)

# if you have an artifact object, you can fetch its metadata directly
artifact = asset.get(local_path)
artifact.fetch()

# if you want to rewrite the existing metadata use force=True
artifact.fetch(force=True)
```

#### How to work with asset alias

```python
# to get the alias of the asset
asset_alias: str = artifact.alias

# to set the alias of the asset
artifact.add_alias(asset_alias)
```

#### How to find an asset

```python
from asset_manager import asset

# to find the asset name with a given alias and class name
asset_name: str = asset.find(class_name=class_name, alias=asset_alias)

# to find the asset name given the asset hash and class name
asset_name: str = asset.find(class_name=class_name, hash=asset_hash)
```

#### How to add inputs to an asset

```python
from asset_manager import ArtifactInputs

# to add an asset to the inputs of an artifact
# input_name must be a string of format <class-name>/<seq-id>/<version>
# give a label to the input using label
# inputs can only be added to the root version (0.0.0) of the asset
artifact.inputs.add(input_name=input_name, label=input_label)

# to commit all the staged inputs to the asset
artifact.upload(commit_message)

# to add inputs remotely without an artifact object
# artifact_name is the name of the asset to which the input is to be added
# inputs can only be added to the root version (0.0.0) of the asset
# artifact_name must be a string of format <class-name>/<seq-id>
# input_name must be a string of format <class-name>/<seq-id>/<version>
# gives a label to the input using label
ArtifactInputs.remote_add(artifact_name=asset_name, input_name=input_name, label=input_label)

# if you already have an Artifact object, you can also use artifact.asset_name
ArtifactInputs.remote_add(artifact_name=artifact.asset_name, input_name=input_name, label=input_label)
```

#### How to list inputs of an asset

```python
from asset_manager import ArtifactInputs

# to list all the inputs of an artifact locally
inputs = artifact.inputs.list()

# to list all the inputs of an artifact from remote
# use remote=True to fetch inputs from remote
inputs = artifact.inputs.list(remote=True)

# use the version to list the inputs of a specific version
inputs = artifact.inputs.list(remote=True, version=version_number)

# to list all the inputs of an asset remotely without an Artifact object
# artifact_name must be a string of format <class-name>/<seq-id>/<version>
inputs = ArtifactInputs.remote_list(artifact_name=asset_name)

# use the version to list the inputs of a specific version
inputs = ArtifactInputs.remote_list(artifact_name=asset_name, version=version_number)
```

#### How to find the size of an asset

```python
from asset_manager import asset

# to get the size of the asset without downloading it
# asset_name can be <class-name>/<seq-id> or <class-name>/<seq-id>/<version>
# without version, it will return the size of the latest version
asset_size = asset.find_size(asset_name)

# use <class-name>/<seq-id>/<version> to get the size of a specific version
asset_size = asset.find_size(asset_version_name)
```

#### How to manage asset Store

```python
# asset store is a place where we keep all the metadata of the assets
# it also keeps a mapping of all the assets and their location you have locally
from asset_manager import asset

# asset store is set automatically when use the asset-manager
# to set the asset store manually at a target location
asset.store.set(target_location)

# to get information about the current asset store
store_info: dict = asset.store.info()

# to clean and remove the invalid asset entries from the asset store
asset.store.prune()

# to clear and remove everything from the asset store
asset.store.clear()
```

#### How to work with asset Configs

```python
# asset configs are a set of user-defined configurations
# these configs are used to modify asset-manager behavior
from asset_manager import asset

# to get information about the current asset configs
current_configs: dict = asset.config.info()

# to set a config value use set()
# both key and value must be strings
asset.config.set(key_string, value_string)

# to reset a config to its default value use reset()
# key must be a string
asset.config.reset(key_string)

# you can reset multiple keys at once
asset.config.reset(key_1, key_2, ...)
```

#### How to work with ArtifactRef

```python
from asset_manager import ArtifactRef

# ArtifactRef is like a proxy Artifact. It can be used to access remote functions of an artifact
# without initializing it locally. Functions are similar to Artifact object.

# to initialize an ArtifactRef object
# asset_version_name must be a string of format <class-name>/<seq-id>/<version>
artifact_ref = ArtifactRef(asset_version_name)

# to get the size of the artifact
size = artifact_ref.size

# to add inputs to the artifact remotely
# input_name must be a string of format <class-name>/<seq-id>/<version>
# give a label to the input using label
artifact_ref.inputs.add(input_name=input_name, label=input_label)

# to list all the inputs of the artifact from remote
inputs = artifact_ref.inputs.list()
```

#### How to find duplicates of an asset

```python
from asset_manager import asset

# initialize or get an artifact
artifact = asset.get_or_init(class_name=class_name, path=local_path)

# check if the artifact is temporary/not uploaded
# find_duplicates() and find_latest_duplicate() can work for both temporary and uploaded artifacts
# but, it is more useful to find duplicates before uploading the artifact
if artifact.is_temp:
    # find all the asset names of the duplicates of that artifact
    # returns a list of asset names format <class-name>/<seq-id>/<version>
    duplicates = artifact.find_duplicates()
    # find the asset name of the latest duplicate of that artifact

    latest_duplicate = artifact.find_latest_duplicate()
```

#### How to check if an asset exists in the cloud

```python
from asset_manager import asset

# to check if an asset exists from a name
# asset_name can be <class-name>/<seq-id> or <class-name>/<seq-id>/<version>
exists = asset.exists(name=asset_name)

# to check if an asset exists from an artifact object
exists = artifact.exists()

# to check if an asset exists from an ArtifactRef object
exists = artifact_ref.exists()
```
