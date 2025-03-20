# Deployment architecture has essentially two main parts

- Enable asset-client to talk to a asset-server of your choosing
- Enable asset-client to operate out of a mounted bucket since the instances are unlikely to have http access

# Communication between asset-client and asset-server

- user also passes a asset-server-url to the config this way we can let the client be agnostic of which server its
  talking to
- We need to use the UserConfigs object, since we need to persist the server-url and mount-configurations across
  multiple sessions

# Mounting a bucket

## How mounting data is retained across sessions

- user passes a bucket mount config using asset set config which is "bucket_url":"mount-path", for multiple, user needs
  to invoke the command multiple times
- during project.activate(), the configs are loaded as environment variable

## How we use the mount information to identify the right storage type

- In the StorageFactory class, which is the gateway to accessing any storage object, we check the mount configurations,
  if any, and ensure
  that we normalize the user passed path to a s3:// or gs:// url so that we can identify the right storage for a given
  url

## How we perform the copy, upload, download operations

- We introduce two new classes AwsHttpHandler and AwsMountHandler
- We move standard s3/botocore calls into the AwsHttpHandler
- We implement the copy, upload, download operations in the AwsMountHandler as if its a local file system
- We create a S3 proxy service that communicates with the asset-server to get blob metadata, etag, md5 etc. For this
  reason we need to pass the ASSET_SERVER_URL as an environment variable, so the plugins can use it
- We create a separate endpoint in the asset-server to handle metadata operations
- The AwSMountHandler will user the S3 proxy service to get the metadata and then perform the operations
- We refactor the StorageMixin to use the AwsHttpHandler and AwsMountHandler based on mounting information

## How we pass all necessary information to the plugins

- For login, login with token etc, we refactored the SettingsAPI to activate user-configs before performing any
  operations
- In `project.activate`, we added an extra method - activate_plugin_env, which sets environment variables such as
  ASSET_SERVER_URL for the plugins
  to use
