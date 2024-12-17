# Hello Asset-Manager

## Hands-on with Asset-Manager

Here we will walk you through the basic commands of asset-manager. We will be using the command-line interface as it
is the primary way to interact with asset-manager. You don't need to know anything about assets, asset-classes, or
asset-projects to get started. We will try to explain them as we go along. So let's get started!

### Setting up the environment

- Make sure you have a python virtual environment with `asset-manager` installed. If not, please refer
  to [Installing Asset-Manager](index.md#installing-asset-manager).
- Let's call our virtual environment `asset-env`. We need to activate the environment to start using asset-manager.
- You can activate the environment using the following command:
- `conda activate asset-env` : for conda users
- `mamba activate asset-env` : for mamba users

### Signing up / logging in

- We will be using the `asset auth` sub-command for signing / logging purposes.
- If you are a new user, you need to sign up for asset-manager. Use the following command with your Roche `username` and
  `email address` to sign up:
- `asset auth signup -u <username> -e <email_address>`
- If you are an existing user, you can just log in using the following command:
- `asset auth login` : using google authentication
- To log out, you can use the following command:
- `asset auth logout`
- after successful login, you will see a `Success` message and the list of projects you have access to.

```bash
Success
Signed in as: <username>
#         Project Name       ID                                    Remote-URL
--------  -----------------  ------------------------------------  --------------------------------------------------------------------------------
0 active  asset_playground   48f686da-1b7b-486f-8db3-c1a8f138df2f  gs://pod_assets_staging/sb/48f686da-1b7b-486f-8db3-c1a8f138df2f/commit
1         rss_data_science   9f2c54a8-b4b0-43e3-b6c9-9df4ffd095ff  gs://pod_assets/sb
(use: asset project activate <project_name> --> to activate a project)
```

### Setting up the project

- By default, all new users will have access to the `asset_playground` project.
- We will be using the `asset project` sub-command to interact with asset-manager projects.
- `asset project list` : to view the list of projects you have access to

```bash
(asset-env) ~ % asset project list
#         Project Name       ID                                    Remote-URL
--------  -----------------  ------------------------------------  --------------------------------------------------------------------------------
0         asset_playground   48f686da-1b7b-486f-8db3-c1a8f138df2f  gs://pod_assets_staging/sb/48f686da-1b7b-486f-8db3-c1a8f138df2f/commit
1 active  rss_data_science   9f2c54a8-b4b0-43e3-b6c9-9df4ffd095ff  gs://pod_assets/sb
(use: asset project activate <project_name> --> to activate a project)
```

- If you see a different active project, you have to activate the `asset_playground` project.
- `asset project activate asset_playground` : to activate `asset_playground`

```bash
(asset-env) ~ % asset project activate asset_playground                        
Success
active project: asset_playground
#         Project Name       ID                                    Remote-URL
--------  -----------------  ------------------------------------  --------------------------------------------------------------------------------
0 active  asset_playground   48f686da-1b7b-486f-8db3-c1a8f138df2f  gs://pod_assets_staging/sb/48f686da-1b7b-486f-8db3-c1a8f138df2f/commit
1         rss_data_science   9f2c54a8-b4b0-43e3-b6c9-9df4ffd095ff  gs://pod_assets/sb
```

### Fetching the class list

- To get started, we need to know the asset-classes available in the project.
- `asset class fetch` : to fetch the list of asset-classes available in the project

```bash
(asset-env) ~ % asset class fetch
fetching asset-classes from remote: gs://pod_assets_staging/sb/48f686da-1b7b-486f-8db3-c1a8f138df2f/commit/asset_classes
downloading asset-class list: 100%|█████████████████████████████████| 32/32 [00:00<00:00, 47.24it/s] done - downloading 32 files took: 0.71 sec
verifying checksum: 100%|████████████████████████████████████████| 32/32 [00:00<00:00, 20394.73it/s] done - verifying 32 files took: 0.00 sec

completed
to view the list of classes: (use: asset class list --> to list all the asset classes)
```

- `asset class list` : to view the list of asset-classes available in the project

```bash
(asset-env) ~ % asset class list
Listing asset-classes
#    Name                         ID                                    Created-By    Created-At
---  ---------------------------  ------------------------------------  ------------  -------------------------
1    mosaic-datasets              3661dd0b-30dd-4154-9761-74ff40d9e7b8  jayachs1      2024/09/23 03-36-40 -0700
2    random_test                  ea75fbb9-472e-4c7c-aff8-9cb418b46cb2  huany172      2023/02/08 00-35-34 -0800
3    huang_test                   a6c25d2a-9bb3-42b5-8392-82b87530361e  huany172      2023/01/11 15-09-22 -0800
4    asset_test_class_guptam      bba30c50-52a6-4cfa-8363-796cc8d10f40  guptam38      2024/05/28 07-50-30 -0700
5    doc_class                    b02a1f74-ecf0-4ed8-849c-9f3b863e04db  chatura9      2024/05/24 15-23-50 -0700
6    mymodel                      b753c656-8f61-4fe9-9bfa-a7cd5577a4bf  chatura9      2024/05/24 15-15-41 -0700
7    read_collapser_config        7b289714-ef41-441a-8898-ba8b760b8360  pachaura      2024/06/14 10-29-22 -0700
8    biswalc_test                 3a02dee0-68da-4030-add5-22a690f1e64e  biswalc       2024/05/28 08-22-40 -0700
9    my_first_asset               dbab14b0-ab40-408a-8a25-2220d62fb003  chatura9      2024/05/21 13-14-05 -0700
10   read_collapser_data          862481b0-7fd1-4845-9148-e9287d1ebddb  pachaura      2024/06/07 14-41-26 -0700
11   test                         dfcfcce7-9a5f-471d-b763-57df82328edf  chatura9      2024/05/27 23-07-50 -0700
12   random_huang_0               3b467151-83cc-408f-9630-e0b3d1b68dd3  huany172      2024/05/28 14-56-10 -0700
13   saurav_test                  92571707-d4e5-4806-8492-8c471f8baa1a  dhars9        2024/05/28 10-08-48 -0700
14   input_class_for_random_test  0385b1ea-d346-4104-8392-4336c04c4f95  guptam38      2024/07/16 03-30-45 -0700
15   test_asset_api               64bbf21b-6355-4f94-82f0-11f5585bcbf2  guptam38      2024/07/01 11-25-41 -0700
16   read_collapser_model         464a678e-bdde-4d43-9ecf-2951e80ff148  pachaura      2024/06/14 10-28-00 -0700
17   huang_test_1                 ca2e1732-ad62-41bd-9520-94e9706d8b64  huany172      2023/01/11 16-21-18 -0800
18   random_huang_1               e6cdc3ad-1ace-4127-890a-d88a4718a69e  huany172      2024/05/28 15-49-25 -0700
19   swarup_data                  3a6541a4-d3f4-43f3-9798-4cad0a264aa8  mahantis      2022/09/08 18-50-34 -0700
20   random-test-ok               681ded55-4172-49cb-b18a-f64d2cd2a5b6  huany172      2024/05/28 22-59-15 -0700
21   mlflow_class                 b9846860-ab35-470d-867e-8ec402f0ee8f  chatura9      2024/05/24 15-21-51 -0700
22   ml_model                     d2049b8b-5fe2-4d54-ac48-c80e90e4819a  chatura9      2024/05/24 15-14-45 -0700
23   asset_test_class             b7ee5967-ea1c-4a5c-8ac5-78e7acbe3bbe  guptam38      2024/05/28 07-49-44 -0700
24   ml_model_class               4a2ee53c-fb31-4546-884d-34df8e85ec67  chatura9      2024/05/24 15-16-31 -0700
25   read_collapser_raw_data      cf62bacf-f1c2-4749-9458-d128a6e2d819  pachaura      2024/07/12 09-40-21 -0700
26   mydata                       3be8f2b4-0a0f-4938-8f0f-fd225d15cf9a  chatura9      2024/05/24 15-18-50 -0700
(use: asset list --class <class-name> --> to list all the assets in a class)
(use: asset class fetch --> to refresh the asset-classes from remote)
(use: asset list --help --> for more details)
```

### Initializing a new asset

- Now that we know the asset-classes available in the project, let's create a new asset.
- We will create a new asset of class type `asset_test_class`.
- It's recommended to use a new directory for each asset to keep things organized.
- Let's create a new directory called `my_new_asset` and navigate to it.
- `asset init asset_test_class` : to initialize a new asset of class type `asset_test_class`

```bash
(asset-env) ~ % mkdir my_new_asset
(asset-env) ~ % cd my_new_asset 
(asset-env) my_new_asset % asset init asset_test_class
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|                                          🅰🆂🆂🅴🆃-🅼🅰🅽🅰🅶🅴🆁                                  |
|                       New asset for class 'asset_test_class' initialized                        |
|                          asset location: /Users/username/my_new_asset                           |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

### Adding files to the asset

- In the previous section, we have initialized a new asset in the `my_new_asset` directory.
- As the asset directory is currently empty, let's add some files to it.
- You can add any files to the asset by simply copying them to the asset directory.
- Let's create some new files with some content to begin with.

```bash
(asset-env) my_new_asset % echo "Hello World." > hello_world.txt
(asset-env) my_new_asset % echo "Asset Manager is awesome." > my_file.txt
```

- After adding the files, you can check the status of the asset using the following command:
- `asset status` : to check the status of the asset

```bash
(asset-env) my_new_asset % asset status
asset: asset_test_class/temp_1727989833
version: temp_1727989833

Untracked files:
	(use: asset add <file>... --> to add files, dirs to asset)
		new:   my_file.txt
		new:   hello_world.txt

(use: asset discard --all --> to discard all staged and unstaged changes)
```

- As you can see, both the files `my_file.txt` and `hello_world.txt` are untracked. We need to add them to the asset.
- Also notice the asset name and version has `temp_` prefix. This means it's a local asset and not been uploaded yet.
- Let's add the `hello_world.txt` file to the asset using the following command:
- `asset add hello_world.txt` : to add the `hello_world.txt` file to the asset

```bash
(asset-env) my_new_asset % asset add hello_world.txt
target: ['hello_world.txt']
collecting source information: ... done
this will add 1 files to the asset, do you wish to continue? options: (y/n), default: [y]: y
creating objects: 100%|██████████████████████████████████████████████| 1/1 [00:00<00:00, 918.19it/s] done
updating object cache: 100%|█████████████████████████████████████████| 1/1 [00:00<00:00, 118.53it/s] done
added 1 new files to asset
list of added:
#    Location           Size    Cloned
---  ---------------  ------  --------
0    hello_world.txt    1 KB         ✓
```

- Let's check the status of the asset again to see the changes:
- `asset status` : to check the status of the asset

```bash
(asset-env) my_new_asset % asset status
asset: asset_test_class/temp_1727989833
version: temp_1727989833

Changes to be committed:
	(use: asset discard --staged <file>... --> to discard changes to a file)
		added:   hello_world.txt

Untracked files:
	(use: asset add <file>... --> to add files, dirs to asset)
		new:   my_file.txt

(use: asset discard --all --> to discard all staged and unstaged changes)
```

- Notice the `hello_world.txt` file is now moved from `Untracked` to staged state.
- Let's add all the untracked files to the asset using the following command:
- `asset add .` : to add all the untracked files in the current directory

```bash
(asset-env) my_new_asset % asset add .
target: ['.']
collecting source information: ... done
this will add 2 files to the asset, do you wish to continue? options: (y/n), default: [y]: y
creating objects: 100%|█████████████████████████████████████████████| 2/2 [00:00<00:00, 1777.62it/s] done
updating object cache: 100%|█████████████████████████████████████████| 2/2 [00:00<00:00, 353.74it/s] done
added 1 new files to asset
list of added:
#    Location       Size    Cloned
---  -----------  ------  --------
0    my_file.txt    1 KB         ✓
found 1 existing file in the asset, list of existing:
#    Location           Size    Cloned
---  ---------------  ------  --------
0    hello_world.txt    1 KB         ✓
```

- Let's check the status one more time to see the changes:
- `asset status` : to check the status of the asset

```bash
(asset-env) my_new_asset % asset status
asset: asset_test_class/temp_1727989833
version: temp_1727989833

Changes to be committed:
	(use: asset discard --staged <file>... --> to discard changes to a file)
		added:   my_file.txt
		added:   hello_world.txt

(use: asset discard --all --> to discard all staged and unstaged changes)
```

- Now both the files are in the staged state and ready to be committed/uploaded.

### Uploading the asset

- After adding the files that we want to include in the asset, we need to commit it by uploading the asset.
- Uploading a new asset will give you a new sequence id and version number.
- `asset upload -m "commit message"` : to upload the asset to remote

```bash
(asset-env) my_new_asset % asset upload -m "Initial commit"
uploading commit: 185ab6dbddd369bcf02e0ac9e8cc1b4b - 'Initial commit'
uploading derived contents
downloading asset-meta data: 100%|████████████████████████████████████| 3/3 [00:00<00:00,  7.79it/s] done - downloading 3 files took: 0.39 sec
verifying checksum: 100%|███████████████████████████████████████████| 3/3 [00:00<00:00, 4545.85it/s] done - verifying 3 files took: 0.00 sec
success
asset upload complete
updated version: 0.0.0
uploading files: 100%|████████████████████████████████████████████████| 2/2 [00:02<00:00,  1.22s/it] 
```

- Let's check the status of the asset after uploading:
- `asset status` : to check the status of the asset

```bash
(asset-env) my_new_asset % asset status
asset: asset_test_class/1
version: 0.0.0
asset is clean, there are no changes
```

- Notice we have a sequence id `1` and version number `0.0.0` for the asset now.
- We can now use the asset-name `asset_test_class/1` to refer to this asset in the future.
- The sequence id might be different for you, so make sure to use the correct sequence id from your output.

### Downloading the asset

- After you have uploaded the asset, you or your team members can easily download it from remote to start working on it.
- To download the asset, you just need to know the asset-name i.e. `asset_test_class/1`.
- The sequence id might be different for you, so make sure to use the correct asset-name from previous section.
- Not specifying the version will download the latest version of the asset.
- If you want to download a specific version, you can specify the version number with the asset-name i.e.
  `asset_test_class/1/0.0.0`.
- Use a new directory to download the asset to keep things organized.
- `asset clone asset_test_class/1` : to download the asset

```bash
(asset-env) ~ % asset clone asset_test_class/1
checking if asset exists (asset_test_class/1): ... done: found asset
all files available, skipping download
asset data exists - skipping download
constructing asset list for class: asset_test_class: ... done
nothing to download
linking objects: 100%|███████████████████████████████████████████████| 2/2 [00:00<00:00, 566.76it/s] done - linking 2 files took: 0.00 sec using linking type: copy
Success
asset: asset_test_class/1 is  cloned and ready to use
use: (cd asset_test_class/1 && asset info) --> to view the asset
```

- This will create a new directory with the asset-name `asset_test_class/1` and download the asset files to it.
- You can now navigate to the asset directory and start working on the asset.
- To view the asset information, you can use the following command:
- `asset info` : to view the asset information

```bash
(asset-env) asset_test_class/1 % asset info
project:      asset_playground
asset:        asset_test_class/1
version:      0.0.0
size:         1 KB
hash:         185ab6dbddd369bcf02e0ac9e8cc1b4b
created_by:   username
created_at:   2024/10/03 14-10-33 -0700
asset id:     0bf398f7-cf13-4212-ae39-251195650424
asset class:  asset_test_class
alias:        None
refs:         []
remote:       gs://pod_assets_staging/sb/48f686da-1b7b-486f-8db3-c1a8f138df2f/commit/assets/b7ee5967-ea1c-4a5c-8ac5-78e7acbe3bbe/1/
cloning:      all files were linked - asset fully cloned
              
#    Location           Size    Cloned
---  ---------------  ------  --------
0    hello_world.txt    1 KB         ✓
1    my_file.txt        1 KB         ✓
(use: asset status --> to view any changes to the asset)
```

- Notice the asset information and the files that are part of the asset. Those are the same files that we created and
  uploaded earlier.

### Updating the asset

- We can update or add any new files to the current asset and upload the changes.
- Let's update the content of the `my_file.txt` file and check the status of the asset.

```bash
(asset-env) asset_test_class/1 % echo "We love Asset Manager." > my_file.txt
(asset-env) asset_test_class/1 % asset status
asset: asset_test_class/1
version: 0.0.0

Changes not staged for commit:
	(use: asset discard --unstaged <file>... --> to discard changes to a file)
	(use: asset update <file>... --> to update un-staged changes to a file)
	(use: asset update --all --> to update all un-staged changes)
		modified:   my_file.txt

(use: asset discard --all --> to discard all staged and unstaged changes)
```

- Notice that the `my_file.txt` file is now `modified` and not staged.
- Let's stage the changes to the file using the following command:
- `asset update my_file.txt` : to stage the changes

```bash
(asset-env) asset_test_class/1 % asset update my_file.txt
collecting source information: ... done
this will add 1 files to the asset, do you wish to continue? options: (y/n), default: [y]: 
creating objects: 100%|██████████████████████████████████████████████| 1/1 [00:00<00:00, 915.59it/s] done
updating object cache: 100%|█████████████████████████████████████████| 1/1 [00:00<00:00, 157.95it/s] done
updated 1 file in the asset, list of updates:
#    Location       Size    Cloned
---  -----------  ------  --------
0    my_file.txt    1 KB         ✓
```

- Let's check the status of the asset again to verify the changes:
- `asset status` : to check the status of the asset

```bash
(asset-env) asset_test_class/1 % asset status
asset: asset_test_class/1
version: 0.0.0

Changes to be committed:
	(use: asset discard --staged <file>... --> to discard changes to a file)
		modified:   my_file.txt

(use: asset discard --all --> to discard all staged and unstaged changes)
```

- Notice the `my_file.txt` file is now in the staged state and ready to be committed/uploaded.
- Let's upload the changes to the asset using the following command:
- `asset upload -m "commit massage"` : to upload the changes to remote

```bash
(asset-env) asset_test_class/1 % asset upload -m "Update my_file.txt"
uploading commit: d423ed565ba2e203169e22dc1d221bd7 - 'Update my_file.txt'
uploading derived contents
downloading asset-meta data: 100%|████████████████████████████████████| 2/2 [00:00<00:00,  8.26it/s] done - downloading 2 files took: 0.24 sec
verifying checksum: 100%|███████████████████████████████████████████| 2/2 [00:00<00:00, 3199.32it/s] done - verifying 2 files took: 0.00 sec
success
asset upload complete
updated version: 0.0.1
uploading files: 100%|████████████████████████████████████████████████| 1/1 [00:01<00:00,  1.85s/it]
```

- As we were on version `0.0.0`, after uploading the changes, the new version is `0.0.1`.
- Notice that modifying the asset does not change the sequence id, only the version number is incremented.
- You can now use the new version name `asset_test_class/1/0.0.1` to refer to this asset in the future.
- The sequence id might be different for you, so make sure to use the correct sequence id from your output.