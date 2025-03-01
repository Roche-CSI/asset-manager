
class AssetState:
    """Upload states of an asset"""
    PENDING = "pending"
    COMMITTING = "committing"
    COMMITTED = "committed"


class ObjectState(AssetState):
    pass


class ContentState:
    """States of the content
    """
    # file added
    PENDING = "pending"
    # upload in progress to staging area
    STAGING = "staging"
    # upload completed to temp area
    STAGED = "staged"
    # renaming in progress to final storage
    # this is done from server
    COMMITTING = "committing"
    # renaming completed
    COMMITTED = "committed"


class EditStatus:
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    UNCHANGED = "unchanged"