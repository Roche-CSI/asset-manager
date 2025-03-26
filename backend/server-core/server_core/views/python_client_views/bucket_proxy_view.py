from functools import wraps

from flask import Blueprint, jsonify, request

from server_core.models.bucket import Bucket

view = Blueprint('bucket_proxy', __name__)


# proxy to perform bucket operations, where client can't access s3/gcs directly


@view.route('', methods=['GET'])
def index():
    return jsonify({'message': 's3 proxy'})


def require_blob_url(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        blob_url = request.json.get('blob_url')
        if not blob_url:
            return jsonify({'error': 'blob_url is required'}), 400
        return f(blob_url, *args, **kwargs)

    return decorated_function


def with_bucket(f):
    @wraps(f)
    def decorated_function(blob_url, *args, **kwargs):
        bucket_url = Bucket.get_bucket_url(blob_url)
        bucket = Bucket.get_or_none(Bucket.bucket_url == bucket_url)
        if not bucket:
            return jsonify({'error': 'bucket not found'}), 404
        return f(bucket, blob_url, *args, **kwargs)

    return decorated_function


@view.route('/list_objects', methods=['POST'])
@require_blob_url
@with_bucket
def list_objects(bucket, blob_url):
    with bucket.permissions():
        if not bucket.storage:
            return jsonify({'error': f'storage not found for url:{blob_url}'}), 404
        return jsonify([blob.to_dict() for blob in bucket.storage.list_blobs(url=blob_url)])


@view.route('/get_object', methods=['POST'])
@require_blob_url
@with_bucket
def get_object(bucket, blob_url):
    with bucket.permissions():
        if not bucket.storage:
            return jsonify({'error': f'storage not found for url:{blob_url}'}), 404
        blob = bucket.storage.get_blob(url_string=blob_url)
        if not blob:
            return jsonify({'error': 'blob not found'}), 404
        return jsonify(blob.to_dict())
