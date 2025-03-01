from server_core.models.utils.model_to_dict import model_to_dict

def delete_records(records, model_class, user):
    if not type(records) is list:
        records = [records]

    for record in records:
        record.delete_instance(user=user, permanently=True)
        exists = model_class.get_if_exists(model_class.id == record.id, include_deleted_records=True)
        assert exists is None


def delete_records_with_ids(record_ids, model_class, user):
    if not type(record_ids) is list:
        record_id = [record_ids]

    for id in record_ids:
        record = model_class.get_if_exists(model_class.id == id)
        if record:
            record.delete_instance(user=user, permanently=True)
            exists = model_class.get_if_exists(model_class.id == record.id, include_deleted_records=True)
            assert exists is None

