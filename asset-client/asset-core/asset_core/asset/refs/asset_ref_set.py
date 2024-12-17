from asset_utils.common import BetterSet
from typing import Callable
from asset_core.plugins import utils, exceptions
from asset_core.server import AssetServer
from asset_core.asset.asset_version import AssetVersion
from .asset_ref import AssetRef


class AssetRefSet(BetterSet):
    asset = None

    def __init__(self, *args, asset=None):
        super().__init__(*args)
        self.asset = asset

    def filter(self, predicate: Callable = None) -> [AssetRef]:
        """returns a dict of assets stored in asset-manifest
        Parameters:
            predicate: lambda function
        """
        if not predicate:
            return list(self)
        return [ref for ref in self if predicate(ref)]

    def de_serialize(self, data: list):
        if not data:
            return
        self.extend(list(map(lambda x: AssetRef.de_serialize(asset=self.asset, data=x), data)))

    def serialize(self):
        return [ref.serialize() for ref in self]

    def add_refs(self, refs, save=False) -> tuple:
        """adds refs, updates states
        Parameters
        ----------
        refs
        save

        Returns
        -------
        tuple:
            (added, existing)
        """
        added, existing = [], []
        for ref in refs:
            if self.add(ref):
                ref.set_state(AssetRef.states.ADD_PENDING)
                added.append(ref)
            else:
                existing.append(ref)

        # update states
        self.update_states(refs)
        if save:
            self.save()
        return added, existing

    def add(self, item):
        """overrides add, if a ref object exists and it has a src_version,
        it means that ref_data is verified from the server - so we need to add it.
        User might inadvertently add a ref which already exists, this will prevent
        any such mistakes.
        """
        if item in self:
            existing: AssetRef = self.get(item)
            # if already verified ref, no need to add again
            if existing.src_version.get("id"):
                return False
        super().add(item=item)
        return True

    def remove_refs(self, refs: [AssetRef], save=False):
        self._edit_restricted = False
        states = self.get_states()
        for ref in refs:
            # update the states
            ref.set_state(ref.states.REMOVE_PENDING, save=True)

        self.set_states(states)
        self._edit_restricted = True
        if save:
            self.save()

    def update_states(self, refs: [AssetRef], save=False):
        updates = {ref.unique_repr: ref.get_state() for ref in refs}
        self.set_states(utils.update_dict(self.get_states(), updates), save)

    def find(self, asset_names: list) -> [AssetRef]:
        """Finds refs corresponding to the asset_names
        Parameters
        ----------
        asset_names: [str]

        Returns
        -------
        [AssetRef]

        """
        result = self.filter(predicate=lambda x: x.src_version.get("name") in asset_names)
        return result

    def get_states(self):
        return self.asset.states_db.get_ref_states()

    def set_states(self, x: dict, save=False):
        if save:
            self.asset.states_db.update(**{"ref_states": x})

    def save(self, states=False, all=True):
        if states:
            self.asset.states_db.update(**{"ref_states": self.get_states()})
        elif all:
            self.asset.db.update(**{"refs": [ref.serialize() for ref in self]})
            states = self.get_states()
            self.asset.states_db.update(**{"ref_states": states})

    def clear(self, save=False):
        if save:
            # clear the state also
            self.asset.states_db.remove_ref_states(keys=[ref.unique_repr for ref in self])
        super().clear()
        if save:
            self.save()

    def is_verified(self):
        """makes sure the asset_refs have correct data.
        The user adds ref using by passing the source_asset_name. It's possible that the source_names
        are incorrect. Typically, when the user adds a ref, we verify the source_names, if internet connection
        is available. If the user is offline, then we verify at the time of uploading the asset.
        """
        for ref in self:
            # if id exists, then it's a valid record in db i.e. verified
            if not ref.src_version or not ref.src_version.get("id"):
                return False
        return True

    def verify_ref_sources(self) -> bool:
        """validates the unverified ref objects with the database.
        Here we check if the src_assets passed by the user are valid and fetch their ids
        """
        un_verified = {}
        for ref in self:
            if not ref.src_version.get("id"):
                un_verified[ref.src_version.get("name")] = ref
        if not un_verified:
            return True

        versions_in_db: dict = AssetServer().find_asset_versions(version_names=list(un_verified.keys()))
        missing = []
        for ver_name in un_verified:
            data = versions_in_db.get(ver_name)
            if data:
                ref: AssetRef = un_verified.get(ver_name)
                ref.src_version = {k: data[k] for k in ["id", "name"]}
            else:
                missing.append(ver_name)

        # save it so that we don't have to verify from beginning again
        self.save()

        if missing:
            raise exceptions.InvalidVersionError(f"unable to create refs, asset(s) not found: {','.join(missing)}")

        return True

    def ref_changes(self) -> tuple:
        """Computes ref additions and removals
        Parameters
        ----------
        seq_id: int
            sequence id of the asset before it was committed. Note that sequence id
            can be temp for assets before their first commit. A sequence id gets assigned
            when the asset is first created in the database. The 'asset' object here will
            already have the accurate sequence id since refs_upload can only happen after
            asset is committed (which assigns the version id). Therefore, in order to know
            if the asset was a temp_asset (before commit), we use the prior seq_id.
        asset: Asset

        Returns
        -------
        tuple: (added, removed)
        """
        added, removed = [], []
        for ref in self:
            if not ref.dst_version.get("id"):
                raise exceptions.ForbiddenRefError("A ref can not be created for a non-committed asset")

        for ref in self:
            if ref.get_state() == ref.states.REMOVE_PENDING:
                removed.append(ref.serialize())
            elif ref.get_state() == ref.states.ADD_PENDING:
                added.append(ref.serialize())

        return added, removed

    def update_temp_refs(self):
        asset = self.asset
        root_version: AssetVersion = asset.root_version()
        if not root_version:
            raise exceptions.ForbiddenRefError("A ref can not be created for a non-committed asset")
        for ref in asset.refs:
            if ref.is_temp:
                ref.dst_version = {"id": root_version.id, "name": root_version.name}
