"""Used only in asset-server"""
import logging

import boto3
from botocore.exceptions import ClientError


def create_presigned_url(credentials: dict,
                         bucket_name: str,
                         object_name: str,
                         expiration=3600):
    """Generate a presigned URL to share an S3 object.

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html

    Parameters
    ----------
    bucket_name : str
        The name of the S3 bucket.
    object_name : str
        The name of the S3 object.
    expiration : int, optional
        Time in seconds for the presigned URL to remain valid. Default is 3600 seconds.

    Returns
    -------
    str or None
        Presigned URL as a string. If an error occurs, returns None.
    """
    s3_client = boto3.client('s3', **credentials)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
