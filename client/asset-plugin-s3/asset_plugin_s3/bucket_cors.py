"""Used only in asset-server"""
import logging

import boto3
from botocore.exceptions import ClientError


def get_bucket_cors(credentials: dict, bucket_name: str):
    """Retrieve the CORS configuration rules of an Amazon S3 bucket.

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-configuring-buckets.html

    Parameters
    ----------
    bucket_name : str
        The name of the S3 bucket.
    credentials : dict
        The credentials to access the S3 bucket.

    Returns
    -------
    list:
        List of the bucket's CORS configuration rules. If no CORS
        configuration exists, return empty list. If error, return None.
    """
    # Retrieve the CORS configuration
    s3 = boto3.client('s3', **credentials)
    try:
        response = s3.get_bucket_cors(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
            return []
        else:
            # AllAccessDisabled error == bucket not found
            logging.error(e)
            return None
    return response['CORSRules']


def set_bucket_cors(credentials: dict, bucket_name: str, origin_url: str):
    """Sets the cors configuration for the bucket.

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-configuring-buckets.html

    Parameters
    ----------
    credentials : dict
        The credentials to access the S3 bucket.
    bucket_name : str
        The name of the S3 bucket.
    origin_url : str
        The origin URL to allow access from.
    """
    # Define the configuration rules
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['Authorization'],
            'AllowedMethods': ['GET'],
            'AllowedOrigins': [origin_url],
            'ExposeHeaders': ['ETag', 'x-amz-request-id'],
            'MaxAgeSeconds': 3000
        }]
    }

    # Set the CORS configuration
    s3 = boto3.client('s3', **credentials)
    s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
