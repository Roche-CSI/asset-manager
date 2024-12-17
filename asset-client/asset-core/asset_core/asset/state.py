class AssetState:
    """Upload states of an asset"""
    PENDING = "pending"
    COMMITTING = "committing"
    COMMITTED = "committed"


class ObjectState(AssetState):
    pass


class EditStatus:
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    UNCHANGED = "unchanged"


class InputState:
    """Upload states of an asset input"""
    ADD_PENDING = "pending"
    ADD_COMMITTING = "committing"
    REMOVE_PENDING = "remove_pending"
    REMOVE_COMMITTING = "remove_committing"
    COMMITTED = "committed"
