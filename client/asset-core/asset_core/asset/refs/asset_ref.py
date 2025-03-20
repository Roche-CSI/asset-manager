from __future__ import annotations

import requests

from asset_core.asset.asset_version import AssetVersion
from asset_core.asset.state import InputState
from asset_core.plugins import exceptions, LoggingMixin
from asset_core.server import AssetServer


class AssetRef(LoggingMixin):
    states = InputState
    asset = None
    id: int
    src_version: dict
    dst_version: dict
    created_by: str
    created_at: str
    label: str
    properties: dict

    def __init__(self, asset=None, **kwargs):
        """
        Parameters
        ----------
        asset: Asset
        id: int
            asset_ref record id
        src_version: int
                source version id
        dst_version: int
                destination i.e. target version id
        src_name: str
                description of reference, currently we are using it to store asset name
        """
        self.asset = asset
        for field in self.__class__.serialize_fields():
            setattr(self, field, kwargs.get(field))
        self.validate()

    def validate(self):
        # TODO: check for self-refs
        # label is required
        if not hasattr(self, 'label') or not self.label:
            raise exceptions.InvalidRefError("required param can not be null: label")
        # both src and dst version are required
        if not self.src_version or not self.dst_version:
            raise exceptions.InvalidVersionError("src_version and dst_version are required for AssetRef")
        # if no id or name, then src_version has not been committed yet
        if not self.src_version.get("id") and not self.src_version.get("name"):
            raise exceptions.InvalidVersionError(msg="src_version: both id and name can not be null")
        # if no id or name, then dst_version has not been committed yet
        if not self.dst_version.get("id") and not self.dst_version.get("name"):
            raise exceptions.InvalidVersionError(msg="dst_version: both id and name can not be null")

    @classmethod
    def create(cls, src_ver_name: str,
               dst_ver_name: str,
               src_ver_id: int = None,
               dst_ver_id: int = None,
               label: str = None,
               properties: dict = None,
               asset=None,
               project_id: str = None,
               remote=False
               ) -> AssetRef:
        """Creates a Ref object. Note: dst_ver_id can be null when user is adding a ref to a newly created asset
        which is yet to be committed in the database.

        Parameters
        ----------
        project_id
        asset
        dst_ver_name
        src_ver_name
        dst_ver_id
        src_ver_id
        label
        properties
        remote: bool
                If true, we can create the ref directly in remote - so we must validate the dst_id as well

        Returns
        -------
        AssetRef object

        """
        project_id = project_id or (asset.asset_class.project if asset else None)
        if not project_id:
            raise exceptions.NoActiveProjectError()
        # verify label is as per class template
        cls.verify_label(label=label)
        # verify source is a valid entry in database
        if not src_ver_id:
            src_ver_name, src_ver_id = cls.get_version_id(project_id=project_id, name=src_ver_name, force=remote)
        if remote and not dst_ver_id:
            # locally, ref can be added to temp asset
            # but for remote, asset must exist in db, so we also verify the dst_name and dst_id
            dst_ver_name, dst_ver_id = cls.get_version_id(project_id=project_id, name=dst_ver_name, force=remote)

        ref = AssetRef(asset=asset,
                       src_version={"id": src_ver_id, "name": src_ver_name},
                       dst_version={"id": dst_ver_id, "name": dst_ver_name},
                       label=label,
                       properties=properties)
        if remote:
            ref = cls._update_in_remote(asset=asset, ref=ref)

        return ref

    @classmethod
    def _update_in_remote(cls, asset, ref: AssetRef):
        add_data = {
            "src_version": ref.src_version.get("id"),
            "dst_version": ref.dst_version.get('id'),
            "label": ref.label,
            "properties": ref.properties
        }
        # server responds with a list of all refs for the target version
        res = AssetServer().update_refs(data={"added": [add_data],
                                              "removed": []})
        # if there is an issue with update_refs - a dict is returned, with success a list is returned.
        if isinstance(res, dict) and res.get("error"):
            raise exceptions.InvalidRefError(msg=res.get("error"))

        for data in res:
            if data.get("src_version").get("id") == ref.src_version.get("id"):
                # check if labels are same, we are allowing multiple refs provided
                # labels are different
                if data.get("label") == ref.label:
                    return AssetRef.de_serialize(asset=asset, data=data)

        raise exceptions.InvalidRefError(f"unable to create ref between version: {ref.src_version.get('name')} "
                                         f"and {ref.dst_version.get('name')}")

    @classmethod
    def get_refs_from_remote(cls, asset_name: str, project_id: str):
        """
        Parameters
        ----------
        asset_name: asset_class/asset_seq/version_number

        Returns
        -------
        """
        # verify its correct name
        asset_comps: dict = AssetVersion.parse_name(asset_name)
        sanitized = AssetVersion.get_name(*[asset_comps.get(k) for k in ["class_name", "seq_id", "version"]])
        res = AssetServer().find_refs(asset_name=sanitized, project_id=project_id)
        res["depends_on"] = [AssetRef.de_serialize(asset=None, data=ref_data) for ref_data in res.get("depends_on", [])]
        res["dependents"] = [AssetRef.de_serialize(asset=None, data=ref_data) for ref_data in res.get("dependents", [])]
        return res, sanitized

    @classmethod
    def verify_label(cls, label: str):
        """Verify if the label meets the class template
        todo: Implement class label template and validation
        """
        if not label:
            raise exceptions.InvalidRefError("required param can not be null: label")

    @classmethod
    def get_version_id(cls, project_id: str, name: str, force=False) -> tuple:
        """
        verifies if the asset name are accurate i.e. they are valid entries in the
        asset database. The user might do a typo or pass a wrong name, so we need to make sure
        they are valid entries.

        Users are allowed to create refs while offline so if the network is not available, we defer
        verification to the time of upload. However, if user is trying to create a remote ref directly
        we enforce that user must be connected to internet

        Parameters
        ----------
        project_id: str
                project id
        name: str
                name of asset version i.e. class_name/seq_id/version_number
        force: bool
                if True, raise exception if remote is not available
        Returns
        -------
        tuple:
            (name, id)
        """
        # verify correct pattern, this will raise error
        asset_comps: dict = AssetVersion.parse_name(name)
        asset_name_with_version = "/".join([asset_comps.get(k) for k in ["class_name", "seq_id", "version"]])
        try:
            # this is a dict {name: version_dict}
            versions: dict = AssetServer().find_asset_versions(project_id=project_id,
                                                               version_names=[asset_name_with_version])
            # create refs for versions that exist
            if asset_name_with_version not in versions:
                raise exceptions.InvalidVersionError(
                    f"unable to create refs, asset not found: {asset_name_with_version}")
            return asset_name_with_version, versions[asset_name_with_version].get('id')
        except requests.ConnectionError as e:
            # its possible user could be adding refs while offline
            if force:
                # force enforce that user must be connected to internet
                msg = "Asset Server not available, make sure you are connected to internet"
                raise exceptions.ServerNotAvailableError(msg)
            cls.logger().info(str(e))
            return asset_name_with_version, None

    @classmethod
    def verify_sources(cls, asset, src_names) -> dict:
        """verifies if the source names are accurate i.e. they are valid entries in the
        asset database. The user might do a typo or pass a wrong name, so we need to make sure
        they are valid entries.
        """
        # verify locally before verifying in server
        for name in src_names:
            # verify that asset name is correct pattern
            asset_comps: dict = AssetVersion.parse_name(name)
            class_name, seq, ver_number = [asset_comps.get(k) for k in ["class_name", "seq_id", "version"]]
            # prevent self refs, src_asset_name and dst_asset_name can't be same
            if asset.__class__.asset_name(class_name=class_name, seq_id=seq) == asset.name:
                raise exceptions.ForbiddenRefError(f"can not create asset-ref:{name}, asset can not reference itself")

        src_data = {}
        missing = []

        try:
            versions: dict = AssetServer().find_asset_versions(src_names)
            # create refs for versions that exist
            for version_name in src_names:
                if version_name in versions:
                    src_data[version_name] = versions[version_name].get('id')
                else:
                    missing.append(version_name)
        except requests.ConnectionError as e:
            cls.logger().info(str(e))
            src_data = {version_name: None for version_name in src_names}

        if missing:
            raise exceptions.InvalidVersionError(f"unable to create refs, asset(s) not found: {','.join(missing)}")

        return src_data

    @classmethod
    def de_serialize(cls, asset, data: dict) -> AssetRef:
        kwargs = data.copy()
        kwargs["asset"] = asset
        return cls(**kwargs)

    def serialize(self, fields=None) -> dict:
        fields = fields or self.__class__.serialize_fields()
        serialized = {key: getattr(self, key) for key in fields}
        return serialized

    @classmethod
    def serialize_fields(cls):
        return ["id",
                "src_version",
                "dst_version",
                "created_at",
                "created_by",
                "label",
                "properties"]

    def get_state(self):
        try:
            return self._state
        except AttributeError:
            self._state = self.asset.states_db.get_ref_states().get(self.unique_repr) if self.asset else None
            if not self._state:
                self._state = self.states.COMMITTED if self.id else self.states.ADD_PENDING
            return self._state

    def set_state(self, x, save=False):
        self._state = x
        if save:
            self.asset.states_db.add_refs_states(**{self.unique_repr: self._state})

    def can_commit(self):
        return self.get_state() != self.states.COMMITTED

    def __eq__(self, other):
        # required to make hashable
        if isinstance(other, AssetRef):
            return self.__hash__() == other.__hash__()
        return False

    def __ne__(self, other):
        # required to make hashable
        return not self.__eq__(other)

    def __hash__(self):
        # required to make hashable
        return hash(self.unique_repr)

    def __repr__(self):
        return self.unique_repr

    @property
    def unique_repr(self):
        """return a unique representation of the ref, important to add more explanation here.
        -  The main user interface for the ref is the source-asset-name, i.e. users will add, modify, delete a ref
           using the source asset name.
        -  source_name is unique, i.e. no two refs in an asset can share the same source_name
        -  its more straight forward to track a ref using its source_name
        Note: source_name is a client side field only and not stored in database

        Note: each ref is bi-directional, so the signature should be the same for both directions
        """
        # return self.src_version.get("name")
        sign = [self.src_version.get("name"), self.dst_version.get("name")]
        sign.sort()
        return "<->".join(sign)

    @property
    def is_temp(self) -> bool:
        """returns True if the ref is pointing to a temp version,
        this happens when a ref is created in a temp asset i.e. before it has been committed
        for the first time.
        """
        return bool(self.dst_version.get("id") is None)
