export const pythonCode = `# How to clone an asset
# clone the asset at the target location
# asset_name is <class-name>/<seq-id> or <class-name>/<seq-id>/<version>
# target_location is your local path where you want the asset to be cloned
# unlike the asset command line, this will not create a dir with <class-name>/<seq-id>
# if you want to use <class-name>/<seq-id> dir, you have to add it to the target_location
from asset_manager import asset, Artifact
artifact: Artifact = asset.clone(name=asset_name, path=target_location)

# How to use an asset
from asset_manager import asset, Artifact
# this assumes that asset is available locally
# local_path is your local path where asset is available
artifact: Artifact = asset.get(local_path)

# How to initialize an asset
from asset_manager import asset, Artifact
# to initialize an asset for class_name at local_path
artifact: Artifact = asset.init(class_name=class_name, path=local_path)
# if you want to re use the existing asset, you can use get_or_init
# this will initialize the asset if it is not already initialized
# if the asset is already initialized, it will return the existing artifact
artifact: Artifact = asset.get_or_init(class_name=class_name, path=local_path)

# How to add files to an asset
# to add files to the asset use a file_path list
# file_path can be relative to the asset path if it is inside the asset directory
artifact.add([file_path_1, file_path_2, ...])
# to add files that are not inside the asset directory use force=True
# this will copy the files to the asset directory first and then add them
artifact.add([file_path_1, file_path_2, ...], force=True)
# to add all the files in the local_path while initializing the asset use add_all=True
# this will add all the files in the asset directory to the asset
artifact: Artifact = asset.init(class_name=class_name, path=local_path, add_files=True)
# to add remote files to an asset use proxy=True
# this will add file or directory from a gs or s3 bucket to the asset
artifact.add(["gs://bucket-name/file-path.txt"], proxy=True)
# to add a remote directory and maintain the directory structure use the directory url
artifact.add(["gs://bucket-name/dir-path"], proxy=True)

# How to update an asset
# after altering any files in an asset you can update the asset
artifact.update()

# How to upload an asset
# check if the asset is ready to be uploaded can_upload()
artifact.can_upload()
# upload the asset to cloud with a commit message
artifact.upload(commit_message)

# How to add alias to an asset
# get the alias of the artifact
artifact.alias
# add alias to the artifact
artifact.add_alias()

# For more, check the documentation at https://laughing-adventure-j886gwp.pages.github.io/python_api/
`

export const bashCode = `#!/bin/bash
# How to create/update an asset
# creates a new asset in the asset-class. asset-class is auto created if needed.
asset init <class-name>
# adds files and directories to the asset
asset add <file/dir>
# removes any added files or directories
asset remove <file/dir>
# adds a reference between two assets
asset refs add --src<src_asset_version> --dst <dst_asset_version> --label <label_description>
# sets an alias. An alias is a user defined primary key for that asset, alias needs to be unique within asset-class.
asset alias add<alias>
# uploads the asset into cloud
asset upload
# discards a local asset before its been uploaded
asset discard

# How to download/use an asset
# this will download the asset from remote (latest version), this will clone the asset inside a directory named <asset-class>\<ordinal>
asset clone <asset-name>
# if you want the asset to be cloned in a specific location and skip creating <asset-class>\<ordinal> directory
asset clone <asset-name> --dir <dirpath>
# use this command to get the updates to an already cloned asset
asset fetch
# to see the list of all versions
asset versions
# to switch to a different version
asset switch --version <version_number>
# to view the contents of an asset (this will also tell you if the asset was cloned successfully or not)
asset info
# to download any additions to the asset (note: asset fetch just pulls the meta-data of the latest updates, 
# the underlying files must be pulled after you switch to the latest version, 
# this is done in the interest of efficiency)
asset download
# to list all peer assets, i.e. assets in the same class
asset list
# to list all assets in a class
asset list --class class-name
# displays the history of the asset i.e. all changes across different versions of the asset
asset history
# displays asset version and any pending changes that are not committed yet
asset status
# lists all the asset classes
asset class list

# Searching / Finding an asset
# to view the unique hash for that asset
asset info --hash
# returns any assets that might exist with the identical data
asset find --class <asset-class> --hash <hash>
# returns any asset with the alias in the given asset-class
asset find --class <asset-class> --alias <alias>

# For more information, check the documentation at https://laughing-adventure-j886gwp.pages.github.io/python_api/
`