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
# Installing Asset-Manager. To install, activate your conda virtual environment
conda create -n <env-name> asset-manager
conda activate <env_name>

# How to start using after installation
# to sign up if you are a first time user
sset auth signup
# to sign in and start using asset-manager
asset auth login
# to open the web-ui of asset-manager (if you prefer)
asset dashboard

# How to use in a headless machine
# note: you must have logged in to asset-manager in your local machine first
# use this command in your local machine to get the user token
asset auth info --token
# use this command in the headless machine to login
asset auth login --token <token>

# Configuring to bypass DNS in pipelines, CI/CD, Kubernetes (for advanced users)
# We frequently face DNS connectivity issues in data/compute pipelines. 
# To get around this problem you can configure asset-manager to use the IP address of asset-server directly. 
# This flag can be set:
export ASSET_SERVER_SKIP_DNS=true

# Projects are workspaces for teams so that they can manage their assets separately. 
# to refresh your credentials and get new projects that you may have been given access to
asset auth refresh
# to list all projects that you have access to
asset project list
# to switch to a different project
asset project activate <project_name>
# to view information about your current active project
asset project info

# For more information, check the documentation at https://laughing-adventure-j886gwp.pages.github.io/python_api/
`