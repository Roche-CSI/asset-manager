import json
import gzip
from typing import Dict, Any
from flask import Request, g


def data_from_request(request: Request) -> Dict[str, Any]:
    """
    Parse data from request,
    if request is GET, parse data from request.args
    if request is POST/PUT/etc., parse data from request.data handling both single and multi part data.
    Args:
        request: Flask request object
    Returns:
        Dict containing parsed request data
    """
    try:
        if request.method == 'GET':
            data = dict(request.args)
        else:
            if request.data:
                # single-part data
                data = json.loads(request.data.decode("utf-8"))
            else:
                # multi-part data
                data = json.loads(request.form.get("data", "{}"))

        if hasattr(g, 'user'):
            data['user'] = g.user

        return data

    except json.JSONDecodeError:
        return {'user': g.user} if hasattr(g, 'user') else {}


def compress_data(data: any):
    return gzip.compress(json.dumps(data).encode('utf-8'), 5)
