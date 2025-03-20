import asyncio
import math
import xml.etree.ElementTree as ET

import aiohttp
import backoff
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

from asset_plugin_s3.aws_auth import AwsAuth
from asset_plugin_s3.transporter.aws_transport_resource import AwsCopyResource
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure


def copy_resources(credentials: dict, resources: [AwsCopyResource]) -> list:
    return asyncio.run(__async_copy_resources(credentials=credentials, resources=resources))


async def __async_copy_resources(credentials: dict, resources: [AwsCopyResource]) -> list:
    result = []
    cred = Credentials(access_key=credentials.get("aws_access_key_id"),
                       secret_key=credentials.get("aws_secret_access_key"))
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        await asyncio.gather(*[__async_copy_resource(session=session,
                                                     credentials=cred,
                                                     resource=resource,
                                                     result=result
                                                     ) for resource in resources])
    return result


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES)
async def __async_copy_resource(session, credentials: Credentials, resource: AwsCopyResource, result: list):
    """Asynchronous function to copy a single resource using multipart or single part copy.

    If the resource has a `multipart_size` attribute, use multipart copy, otherwise use single part copy.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp client session.
    credentials : Credentials
        AWS credentials.
    resource : AwsCopyResource
        The resource to be copied.
    result : list
        List to store the result.
    """
    if resource.multipart_size:
        await __multi_part_copy(session, credentials, resource)
    else:
        await __single_part_copy(session, credentials, resource)

    result.append(resource.dst)
    resource.on_transfer_complete(resource.dst)


async def __single_part_copy(session, credentials: Credentials, resource: AwsCopyResource):
    """Asynchronous function to copy a single part.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp client session.
    credentials : Credentials
        AWS credentials.
    resource : AwsCopyResource
        The resource to be copied.
    """
    signed_headers = part_copy_headers(credentials=credentials,
                                       resource=resource)
    await session.put(convert_url(resource.dst_url), headers=signed_headers)


async def __multi_part_copy(session, credentials: Credentials, resource: AwsCopyResource):
    """Asynchronous function to copy multiple parts.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp client session.
    credentials : Credentials
        AWS credentials.
    resource : AwsCopyResource
        The resource to be copied.

    References
    ---------
    https://docs.aws.amazon.com/AmazonS3/latest/API/API_UploadPartCopy.html
    """
    # TODO: add the `multipart_size` to the copy object metadata to be used for ETag calculation
    # start the multipart copy
    params = {'uploads': ''}
    signed_headers = create_complete_headers(credentials=credentials,
                                             resource=resource,
                                             params=params)
    async with session.post(convert_url(resource.dst_url),
                            params=params,
                            headers=signed_headers) as response:
        content = await response.content.read()
        root = ET.fromstring(content.decode('UTF-8'))
        upload_id = root.findtext("{*}UploadId")

    # copy all the parts
    copy_responses = []
    tasks = get_multipart_copy_tasks(credentials, resource, session, upload_id)
    responses = await asyncio.gather(*tasks)
    for response in responses:
        copy_responses.append(await response.content.read())

    # end the multipart copy
    data = multipart_xml_data(copy_responses)
    params = {'uploadId': upload_id}
    signed_headers = create_complete_headers(credentials=credentials,
                                             resource=resource,
                                             params=params,
                                             data=data)
    await session.post(convert_url(resource.dst_url),
                       params=params,
                       data=data,
                       headers=signed_headers)


def convert_url(blob_url) -> str:
    """Function to convert blob URL.

    Parameters
    ----------
    blob_url : str
        The blob URL.

    Returns
    -------
    str
        The converted URL.

    Examples
    --------
    https://aws-example-bucket.s3.amazonaws.com/asset_tool/test_data/asset_client/sample_files/model.yml
    """
    url_format = "https://{}.{}.amazonaws.com/{}"
    return url_format.format(blob_url.bucket, blob_url.host, blob_url.path)


def get_multipart_copy_tasks(credentials, resource, session, upload_id):
    """Function to create async multipart copy tasks.

    Parameters
    ----------
    credentials : dict
        AWS credentials.
    resource : AwsCopyResource
        The resource to be copied.
    session : aiohttp.ClientSession
        The aiohttp client session.
    upload_id : str
        The upload ID.

    Returns
    -------
    list
        List of tasks.
    """
    tasks = []
    for part_number in range(1, math.ceil(resource.size / resource.multipart_size) + 1):
        first_byte = resource.multipart_size * (part_number - 1)
        last_byte = min(resource.multipart_size * part_number - 1, resource.size - 1)
        params = {'partNumber': str(part_number), 'uploadId': upload_id}
        source_range = f"bytes={first_byte}-{last_byte}"
        signed_headers = part_copy_headers(credentials=credentials,
                                           params=params,
                                           resource=resource,
                                           source_range=source_range)
        tasks.append(session.put(convert_url(resource.dst_url),
                                 params=params,
                                 headers=signed_headers))
    return tasks


def create_complete_headers(credentials: Credentials, resource, params, data=None):
    """Function to create headers for the start and end of the multipart copy.

    Parameters
    ----------
    credentials : Credentials
        AWS credentials.
    resource : AwsCopyResource
        The resource to be copied.
    params : dict
        The parameters.
    data : str, optional
        The data.

    Returns
    -------
    dict
        The headers.
    """
    request = AWSRequest(method="POST",
                         url=convert_url(resource.dst_url),
                         params=params,
                         data=data)
    request.context["payload_signing_enabled"] = False
    AwsAuth(credentials, service_name="s3", region_name="us-east-1").add_auth(request)
    return request.headers


def part_copy_headers(credentials: Credentials, resource, params: dict = None, source_range=None):
    """Function to create part copy headers.

    Parameters
    ----------
    credentials : Credentials
        AWS credentials.
    resource : AwsCopyResource
        The resource to be copied.
    params : dict, optional
        The parameters.
    source_range : str, optional
        The source range.

    Returns
    -------
    dict
        The headers.

    Notes
    -----
    When you use a general endpoint, AWS routes the API request to 'us-east-1' which is the default Region for API calls.

    References
    ---------
    https://docs.aws.amazon.com/AmazonS3/latest/API/API_UploadPartCopy.html
    """
    request = AWSRequest(
        method="PUT",
        url=convert_url(resource.dst_url),
        params=params,
        headers={
            'x-amz-copy-source': convert_url(resource.src_url),
            'x-amz-content-sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        })
    if source_range:
        request.headers['x-amz-copy-source-range'] = source_range
    AwsAuth(credentials, service_name="s3", region_name="us-east-1").add_auth(request)
    return request.headers


def multipart_xml_data(xml_responses: list) -> bytes:
    """Function to create multipart XML data.

    Parameters
    ----------
    xml_responses : list
        List of XML responses.

    Returns
    -------
    bytes
        The XML data.
    """
    output_root = ET.Element("CompleteMultipartUpload")
    for i, xml_response in enumerate(xml_responses):
        root = ET.fromstring(xml_response.decode('UTF-8'))
        e_tag = root.findtext("{*}ETag")
        part = ET.SubElement(output_root, "Part")
        ET.SubElement(part, "PartNumber").text = str(i + 1)
        ET.SubElement(part, "ETag").text = e_tag
    return ET.tostring(output_root, encoding='utf8', method='xml')
