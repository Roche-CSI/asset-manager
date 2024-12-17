### Uploading the Asset

**Check if the BaseAsset can be uploaded.**
In order to be eligible for upload, an BaseAsset must have a designated storage location which it inherits from the asset_class it belongs to.

- Check if the asset has a class_id, if not - request asset_server for id of the asset_class
- The request to asset_server must include class_name
- asset_server receives the request, checks if an asset_class exists for the given name. If not, the asset_server creates an asset_class.
- client receives the class_id and top_hash from the asset_server and updates the asset-manifest
- BaseAsset is now eligible for upload
 
<img src="../../imgs/asset_upload/asset_class_create.jpg" class="image"/>
  
  
  
has a class_id and top_hash, if


* Upload the Contents to Staging Area