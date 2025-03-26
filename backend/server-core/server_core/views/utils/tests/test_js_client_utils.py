import json

import pytest
from flask import Flask, g, request

from server_core.views.utils.view_utils import data_from_request


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


@pytest.fixture
def mock_user():
    return {"id": 1, "email": "test@example.com"}


class TestDataFromRequest:
    def test_get_request_empty(self, app):
        """Test GET request with no parameters"""
        with app.test_request_context('/?'):
            data = data_from_request(request)
            assert data == {}

    def test_get_request_with_params(self, app):
        """Test GET request with parameters"""
        with app.test_request_context('/?name=test&age=25'):
            data = data_from_request(request)
            assert data == {'name': 'test', 'age': '25'}

    def test_get_request_with_user(self, app, mock_user):
        """Test GET request with user in g"""
        with app.test_request_context('/?name=test'):
            g.user = mock_user
            data = data_from_request(request)
            assert data == {'name': 'test', 'user': mock_user}

    def test_post_request_single_part(self, app):
        """Test POST request with single-part data"""
        test_data = {'key': 'value'}
        with app.test_request_context(
                method='POST',
                data=json.dumps(test_data),
                content_type='application/json'
        ):
            data = data_from_request(request)
            assert data == test_data

    def test_post_request_multi_part(self, app):
        """Test POST request with multi-part form data"""
        test_data = {'key': 'value'}
        with app.test_request_context(
                method='POST',
                data={'data': json.dumps(test_data)},
        ):
            data = data_from_request(request)
            assert data == test_data

    def test_post_request_with_user(self, app, mock_user):
        """Test POST request with user in g"""
        test_data = {'key': 'value'}
        with app.test_request_context(
                method='POST',
                data=json.dumps(test_data),
                content_type='application/json'
        ):
            g.user = mock_user
            data = data_from_request(request)
            assert data == {**test_data, 'user': mock_user}
            assert data.get('user') == mock_user

    def test_invalid_json_data(self, app):
        """Test handling invalid JSON data"""
        with app.test_request_context(
                method='POST',
                data='invalid json',
                content_type='application/json'
        ):
            data = data_from_request(request)
            assert data == {}

    def test_invalid_json_with_user(self, app, mock_user):
        """Test handling invalid JSON data with user in g"""
        with app.test_request_context(
                method='POST',
                data='invalid json',
                content_type='application/json'
        ):
            g.user = mock_user
            data = data_from_request(request)
            assert data == {'user': mock_user}

    def test_put_request(self, app):
        """Test PUT request"""
        test_data = {'key': 'value'}
        with app.test_request_context(
                method='PUT',
                data=json.dumps(test_data),
                content_type='application/json'
        ):
            data = data_from_request(request)
            assert data == test_data

    def test_empty_post_request(self, app):
        """Test POST request with no data"""
        with app.test_request_context(method='POST'):
            data = data_from_request(request)
            assert data == {}

    def test_none_data_in_form(self, app):
        """Test POST request with None in form data"""
        with app.test_request_context(
                method='POST',
                data={'data': None}
        ):
            data = data_from_request(request)
            assert data == {}

    def test_post_request_with_args(self, app):
        """Test POST request with None in form data"""
        with app.test_request_context('/?user=user1',
                                      method='POST',
                                      data={'data': None}
                                      ):
            data = data_from_request(request)
            assert data == {'user': 'user1'}

    @pytest.mark.parametrize('method', ['POST', 'PUT', 'PATCH', 'DELETE'])
    def test_different_http_methods(self, app, method):
        """Test different HTTP methods"""
        test_data = {'key': 'value'}
        with app.test_request_context(
                method=method,
                data=json.dumps(test_data),
                content_type='application/json'
        ):
            data = data_from_request(request)
            assert data == test_data
