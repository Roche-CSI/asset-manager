import pytest
import json


@pytest.fixture(scope="module")
def classes_data(test_app):
    """need the test_app fixture for making db transactions"""
    return [
        "genetics",
        "gene_data",
        "dl_training",
        "bio_nlp",
        "ac_modeling",
        "imaging"
    ]


def test_asset_class_post(test_app, classes_data, test_project):
    """create asset classes"""
    for class_name in classes_data:
        data = {'class_name': class_name, 'user': 'user1', 'project': str(test_project.id)}
        res: dict = test_app.post('/asset_class', follow_redirects=True, data=json.dumps(data))
        assert res.status_code == 201  # not allowed
        res = json.loads(res.data)
        assert res.get("name") == class_name
