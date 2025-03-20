from .add import AddToAsset
from .clone import CloneAsset
from .commit import CommitMessage
from .cp import CopyObject
from .dashboard import AssetDashboard
from .debug import DebugAsset
from .delete import AssetDelete
from .diff import AssetDiff
from .discard import AssetDiscard
from .download import DownloadAsset
from .fetch import FetchAsset
from .find import AssetFind
from .hash import ComputeHashAction
from .history import AssetHistory
from .info import AssetInfo
from .init import InitAsset
from .list import ListAssets
from .pull import AssetPull
from .remote import RemoteInfo
from .remove import RemoveFromAsset
from .report import AssetReport
from .restore import AssetRestore
from .status import AssetStatus
from .switch import AssetSwitch
from .tree import AssetTree
from .union import AssetUnion
from .update import UpdateAsset
from .upload import UploadAsset
from .user_prompt_setting import UserPromptSetting
from .versions import AssetVersions


def get_actions():
    return [
        InitAsset(),
        AddToAsset(),
        RemoveFromAsset(),
        ListAssets(),
        AssetSwitch(),
        UploadAsset(),
        DownloadAsset(),
        CommitMessage(),
        AssetVersions(),
        FetchAsset(),
        AssetDiff(),
        AssetHistory(),
        RemoteInfo(),
        AssetStatus(),
        AssetInfo(),
        AssetDiscard(),
        CloneAsset(),
        UpdateAsset(),
        UserPromptSetting(),
        AssetFind(),
        ComputeHashAction(),
        AssetDashboard(),
        AssetTree(),
        AssetUnion(),
        AssetReport(),
        DebugAsset(),
        CopyObject(),
        AssetPull(),

        # AssetDelete(),
        # AssetRestore()
    ]
