from asset_core.objects.object import Object


class GroupMemberObject(Object):
    type = "group_member"
    parent_obj = None  # parent object, this is used for complex objects such as sql-object or group-object

    @classmethod
    def serialize_fields(cls):
        return [
            "id",
            "content",
            "type"
        ]

    def serialize(self, fields: list = None) -> dict:
        """Serializes the object for writing to yaml

        Parameters
        ----------
        fields: list (Optional)
            if passed, only those fields are serialized - else all fields are serialize

        Returns
        -------
        dict

        """
        # note: we don't need fields such as created_at etc. since we are writing all of these to a file
        # derived objects are meant be used for large-assets i.e. 100,000 files or more, we need to optimize
        # and remove unnecessary fields
        content_fields = ["id", "hash", "mime_type", "size", "meta"]
        serialized = super().serialize(*(fields or []))
        serialized["content"] = {key: serialized["content"][key] for key in content_fields}
        return serialized

    def add_to_asset(self, asset, **kwargs):
        self.asset = asset
        # unlike regular objects, the member objects are not added to the asset.objects at the time of creation
        # however, we add the contents to asset contents
        self.content = self.asset.contents.add_content(content=self.content)
        self.content.add_to_asset(asset=asset, object=self)
        self.set_state(self.__class__.states.PENDING)

    @property
    def can_update(self):
        return False
