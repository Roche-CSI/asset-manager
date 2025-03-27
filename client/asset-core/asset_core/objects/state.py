class ObjectState:
    """Upload states of an asset"""
    PENDING = "pending"
    COMMITTING = "committing"
    COMMITTED = "committed"


class ObjectEditStatus:
    MODIFIED = "modified"
    DELETED = "deleted"
    # RENAMED = "renamed"
    UNCHANGED = "unchanged"
