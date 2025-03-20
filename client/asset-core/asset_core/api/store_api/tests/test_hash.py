import os

from asset_core.api.store_api import ContentHashAPI


def test_content_hash(store, project_root, capfd):
    test_data = {
        "csvs/customers.csv": "md5_eIlrw2PBTOr3VKXLHClkTQ==",
        "jpegs/photo-1522364723953-452d3431c267.jpg": "md5_4N7Mr93Wbtzm5j104ol0Mw==",
        "jsons/web_app.json": "md5_ARwG99V78wJ7IrgOtQCP4A==",
        "yamls/invoice.yaml": "md5_eyAkfZtBeaxG/cQFPiDbEg==",
    }
    api = ContentHashAPI(store=store)
    file_path = os.path.join(project_root, "test_data", "file_types")
    for src, expected in test_data.items():
        src = os.path.join(file_path, src)
        api.content_hash(src)
        out, err = capfd.readouterr()
        assert expected in out
        assert not err
