import gzip
import json
from typing import Dict, Any

from flask import Request, g


def data_from_request(request: Request) -> Dict[str, Any]:
    """
    Parse data from both request.args and request.data, combining them into a single dictionary.
    If user is present in g (extracted from authorization token), add user to the data.
    Args:
        request: Flask request object
    Returns:
        Dict containing combined request data
    """
    try:
        data = dict(request.args)

        if request.data:
            try:
                # single-part data
                json_data = json.loads(request.data.decode("utf-8"))
                data.update(json_data)
            except json.JSONDecodeError:
                pass

        # Handle multi-part form data
        if request.form:
            form_data = request.form.get("data")
            if form_data:
                try:
                    json_form_data = json.loads(form_data)
                    data.update(json_form_data)
                except json.JSONDecodeError:
                    pass

        # Add user if present in g
        if hasattr(g, 'user'):
            data['user'] = g.user

        return data

    except Exception:
        # Fallback return with at least user data if available
        return {'user': g.user} if hasattr(g, 'user') else {}


def compress_data(data: any):
    return gzip.compress(json.dumps(data).encode('utf-8'), 5)
