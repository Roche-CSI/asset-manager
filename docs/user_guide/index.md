# Quick Start

## How to install and Use Asset-Manager

### Installing Asset-Manager

`shell
pip install asset-manager
`

### How to start using after installation

#### Sign up and Login to Asset-Manager

- `asset auth signup` : to sign up if you are a first time user
- `asset auth login` : to sign in and start using asset-manager
- `asset dashboard`: to open the web-ui of asset-manager (if you prefer)
- `asset auth logout`: to logout from asset-manager

#### How to use in a headless machine

Get the user token from your local machine and use it in the headless machine to login. You must be logged in to get the
token.

- `asset auth info --token`: use this command in your local machine to get the user token
- `asset auth login --token <token>`: use this command in the headless machine to login

#### Configuring to bypass DNS in pipelines, CI/CD, Kubernetes (` for advanced users`)

We frequently face DNS connectivity issues in data/compute pipelines. To get around this problem you can configure
asset-manager to use the IP address of asset-server directly. This flag can be set:

- `export ASSET_SERVER_SKIP_DNS=true`

## What is an asset

- An asset holds a collection of files together as a single atomic unit. You can use assets to store, retrieve and share
  files.
- Assets are immutable objects and version controlled. Any changes you make to an asset is automatically updated as a
  different version.
- Assets name is in the format `<class-name>/<ordinal>`. The ordinal is a sequence id that is auto-generated every time
  you initialize a new asset.

## What is an asset-class

- An asset-class is a grouping of similar types of assets. For example, you can use the asset-class `ml-models` to store
  all machine learning models. Another
  example could be `training-data` asset-class that holds all model training data.
- The asset-class architecture allows us to conveniently add a lot of the features as follows:
    - easy naming convention for assets i.e. `<class-name>/<ordinal>`
    - visualization rules for assets, we can create custom visualization rules for different types of assets
    - validation rules for assets

#### How to work with asset-class

- `asset class init <class-name>` : opens up the asset-dashboard to create a new asset-class.
- `asset class fetch` : fetches the class-list and all the metadata of the asset-classes of the current project.
- `asset class list` : lists all the asset-classes in the current project.
- `asset class info -n <class-name>` : to view the info of a specific asset-class.

## How to create/update an asset

#### Initialize a new asset

- `asset init <class-name>` : creates a new asset in your current directory.

Make sure you are using a valid and existing `asset-class` name.

#### Modify an asset

- `asset add <file/dir>` : adds files and directories to the asset. Make sure these files are in the asset directory.
- `asset remove <file/dir>` : removes any added files or directories
- `asset inputs add <asset_version_name> --label<label_description>` : adds reference of another asset as an input to
  the current asset. Currently, inputs can only be added to the base version of the asset.
- `asset alias add <alias>` : sets an alias for the asset. An alias is a user defined primary key for that asset, alias
  needs to be unique within asset-class.

#### Commit and Upload

- `asset status` : to view the status of the files in the asset
- `asset update <file_name>` : to commit the changes to a file
- `asset upload -m <commit_msg>` : uploads the asset into cloud and creates a new version
- `asset discard` : discards staged or unstaged changes to the asset

## How to download / use an asset

- `asset clone <asset-name>` : this will download the latest version of the asset from remote inside a directory named
  `<asset-class>\<ordinal>`

#### Run the following commands from the asset directory

- `asset info` : to view the info and contents of an asset (this will also tell you if the asset was cloned successfully
  or not)
- `asset fetch`: use this command to get the updates to an already cloned asset
- `asset versions`: to see the list of all versions
- `asset switch --version <version_number>` : to switch to a different version
- `asset download`: to download any additions to the asset (`note`: asset fetch just pulls the meta-data of the latest
  updates, the underlying files must be pulled after you switch to the latest version, this is done in the interest of
  efficiency)
- `asset list` : to list all peer assets, i.e. assets in the same class
- `asset list --class class-name` : to list all assets in a class
- `asset history` : displays the history of the asset i.e. all changes across different versions of the asset
- `asset status` : displays asset version and any pending changes that are not committed yet
- `asset class list`: lists all the asset classes of the current project

## Searching / Finding an asset

assets are hashable, therefore we can compare if two different assets are identical or not

- `asset info --hash`: to view the unique hash for that asset
- `asset find --class <asset-class> --hash <hash>`: returns the asset-name with the given hash
- `asset find --class <asset-class> --alias <alias>`: returns the asset-name with the given alias
- `asset find --size <asset-name>`: returns the size of the asset, will use the latest version if no version is
  specified

## What is a Project

Projects are workspaces for teams so that they can manage their assets separately. Projects give you the ability to
define the following

- storage location of assets, i.e. a blob store location such as google bucket or aws s3 bucket
- team members, i.e. users who can access your assets

#### How to work with projects

We have created the `asset-playground` project as a default workspace for all users to try out asset-manager. Once your
team creates their own project you can get access to it by using the following commands:

- `asset project list`: to list all projects that you have access to
- `asset project activate <project_name>`: to activate a project and start working on it
- `asset project info`: to view information about your currently active project

[//]: # (###Listing assets)

[//]: # ()

[//]: # (Note the difference between ***asset vs asset&#40;s&#41;***.)

[//]: # ()

[//]: # (- `assets list --classes` : lists all asset-classes in local repo)

[//]: # (- `assets list --classes -r`: lists all asset-classes in remote repo)

[//]: # (- `assets fetch --classes`: pulls all remote changes to asset-classes into local)

[//]: # (- `assets list <class-name>` : lists all the assets in the asset-class from local repo)

[//]: # (- `assets list <class-name> -r` : lists all the assets in the remote repo.)

[//]: # (- `assets fetch <class-name>` : pulls all remote changes into local)

[//]: # (- `assets diff <asset1> <asset2>` : displays the differences between 2 assets)

## What is an Asset Store

The Asset Store is the global cache of all the assets and their metadata in your machine.

- There is only one active asset-store for your machine.
- `asset-manager` uses the asset-store to perform optimizations while uploading/downloading assets, shared files between
  different assets are cloned from the local `asset-store` instead of fetching from the remote.
- It maintains a mapping of all local assets and their locations in the machine.
- Asset-store also stores the class-list and class-metadata for all the asset-classes for all your projects.
- Any changes you make to your asset are isolated and can be reversed until you commit those changes.
- Shared files (between different assets or different versions) don't occupy extra disk space up until you make any
  modifications.
- Shout out to docker, to achieve this, we take an approach that is similar to how docker manages images and containers
  in your machine.

#### How to work with the asset-store

- `asset store info`: to view the information about the active asset-store
- `asset store set <store-path>`: to set the asset store to any specific location
- `asset store prune`: to remove any invalid asset entries from the asset-store
- `asset store clear`: clears all files in the store. Warning: Don't do this unless you must. You can still use your
  cloned assets but note that you will need to do `asset download` again to switch a different version of the asset.

## Admin Commands (to be implemented)

`Note`: when you delete asset / asset-clas, they are flagged for deletion and will be permanently
deleted after 30 days. You can undo delete within that time.

#### Deleting an Asset / Asset Class

- `asset delete <asset-id>` : deletes an asset from your local cache
- `asset delete --alias <alias>` : deletes an asset from your local cache using its alias

#### Deleting an Asset / Asset Class

- `asset schedule-deletion <asset-name> <days:optional>`: deletes an assets after a specified number of days. If
  the `days` is not specified, it will default to 30 days. Any value less than 30 days will be treated as 30 days.
- `asset class delete <class-name>`: removes the asset-class from local cache as well as in the remot along with all the
  assets and its related content from the repo. ( admin option - may be not needed yet )

#### Restoring a deleted Asset / Asset Class

- `asset restore <asset-name>` : restores a deleted asset, you will need to do `assets fetch <class-name>` to pull from
  remote
- `asset restore --alias <asset-name>` : restores a deleted asset, you will need to do `assets fetch <class-name>` to
  pull from remote
- `asset restore --class <class-name>` : restores a deleted asset-class, you will need to do `assets fetch --classes` to
  pull all classes again from remote
