import os
import subprocess

from asset_core.api.tests.e2e_tests.base_e2e import BaseE2ETest


# don't add test prefix here, we don't want pytest to run this

def get_git_root():
    try:
        # Run git command to get top-level directory
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True, check=True)
        # The output will be in result.stdout
        git_root = result.stdout.strip()
        return git_root
    except subprocess.CalledProcessError as e:
        # Handle errors if the command fails
        print(f"Error: {e}")
        return None


class CloneSpecificVersion(BaseE2ETest):
    desc = "cloning remote asset"
    cmd = [
        "clone dsaswe_test/23/0.0.5 ",  # remove any existing
    ]
    out = "cloned and ready to use"
    error = ""


class CloneAssetLatestVersion(BaseE2ETest):
    desc = "cloning remote asset"
    cmd = [
        "clone dsaswe_test/23 --force",  # remove any existing
    ]
    out = "cloned and ready to use"
    error = ""


class GetVersionSize(BaseE2ETest):
    desc = "get asset version size"
    cmd = [
        "find --size {asset_name}"
        # "find --size v2_objects/4/0.0.1"
    ]
    out = "success: size"
    error = ""


# class DiscardMeta(BaseE2ETest):
#     desc = "discard meta changes"
#     cmd = [
#         "meta discard"
#     ]
#     out = "success: meta changes discarded"
#     error = ""
#
#
# class ReAddExistingMeta(BaseE2ETest):
#     desc = "re-adding existing meta file"
#     cmd = [
#         "meta discard",  # remove any existing
#         "meta add summary_dict.json",
#         "meta add summary_dict.json",
#     ]
#     out = "Entity already exists"
#     error = ""
#
#
# class AddInvalidMeta(BaseE2ETest):
#     desc = "adding invalid meta file"
#     cmd = [
#         "meta discard",  # remove any existing
#         "meta add graph_version.txt"
#     ]
#     out = "Invalid meta file type"
#     error = ""
#
#
# class UploadAddedMeta(BaseE2ETest):
#     desc = "upload meta file"
#     cmd = [
#         "meta discard",  # remove any existing
#         "meta add summary_dict.json",
#         "meta upload"
#     ]
#     out = "success: meta file uploaded"
#     error = ""
#
#
# class RemoveUploadedMeta(BaseE2ETest):
#
#     desc = "upload removed meta file"
#     cmd = [
#         "meta discard",  # remove any existing
#         "meta add summary_dict.json",
#         "meta upload",
#         "meta remove summary_dict.json",
#         "meta upload"
#     ]
#     out = "success: meta file removed"
#     error = ""
#
#
# class RemoveAddedMeta(BaseE2ETest):
#     desc = "remove added meta file"
#     cmd = [
#         "meta discard",  # remove any existing
#         "meta add summary_dict.json",
#         "meta remove summary_dict.json",
#     ]
#     out = "success"
#     error = ""
#
#
# class RemoveNonExistingMeta(BaseE2ETest):
#     desc = "remove non-existing meta file"
#     cmd = [
#         "meta discard",  # remove any existing
#         "meta remove summary_dict.json",
#     ]
#     out = "Entity not found"
#     error = ""
#
#
# class MetaInfoRemote(BaseE2ETest):
#     desc = "get meta info remote"
#     cmd = [
#         "meta info --r"
#     ]
#     out = "Meta info"
#     error = ""
#
# class SearchAssetMeta(BaseE2ETest):
#     desc = "search asset meta"
#     cmd = [
#         "find --class rnn_model_sb --meta validation.loss.time.3=1684219370.0"
#     ]
#     out = "success: found"
#     error = ""

# set this to the root of the project

TESTS = [
    # CloneAssetVersion,
    # CloneAssetLatestVersion
    (GetVersionSize, {"asset_name": "ml_dataset/1"}),
    # DiscardMeta,
    # AddInvalidMeta,
    # ReAddExistingMeta,
    # RemoveAddedMeta,
    # RemoveNonExistingMeta,
    # UploadAddedMeta,
    # MetaInfoRemote,
    # SearchAssetMeta,
    # RemoveUploadedMeta,
]

WORKING_DIR = "/Users/mahantis/am_demo"

if __name__ == "__main__":
    os.environ["CODE_DIR"] = get_git_root()
    for test in TESTS:
        target, params = test
        t = target(working_dir=WORKING_DIR, params=params)
        t.run()
