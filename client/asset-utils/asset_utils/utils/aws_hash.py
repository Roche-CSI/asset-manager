import hashlib
import os

from asset_utils.utils.file_utils import FileUtils

"""
https://teppen.io/2018/10/23/aws_s3_verify_etags/
"""

AWS_CLI_BOTO3_PART_SIZE = 8 * 1024 * 1024  # 8MB
S3CMD_PART_SIZE = 15 * 1024 * 1024  # 15MB


def factor_of_1MB(filesize, num_parts):
    x = filesize / int(num_parts)
    y = x % 1048576
    return int(x + 1048576 - y)


def calc_etag(input_file, part_size):
    md5, num_parts = calc_md5(input_file, part_size)
    return md5 + '-' + str(num_parts)


def calc_bytes_etag(file_bytes, part_size):
    md5, num_parts = calc_bytes_md5(file_bytes, part_size)
    return md5 + '-' + str(num_parts)


def calc_md5(input_file, part_size) -> tuple:
    md5_digests = []
    with open(input_file, 'rb') as f:
        for chunk in iter(lambda: f.read(part_size), b''):
            md5_digests.append(hashlib.md5(chunk).digest())
    # return the md5 hash of all the md5 md5_digests and the number of parts
    return hashlib.md5(b''.join(md5_digests)).hexdigest(), len(md5_digests)


def calc_bytes_md5(file_bytes, part_size) -> tuple:
    md5_digests = []
    start = 0
    while start < len(file_bytes):
        chunk = file_bytes[start:start + part_size]
        start += part_size
        md5_digests.append(hashlib.md5(chunk).digest())
    # return the md5 hash of all the md5 md5_digests and the number of parts
    return hashlib.md5(b''.join(md5_digests)).hexdigest(), len(md5_digests)


def possible_part_sizes(file_size, num_parts):
    return lambda part_size: part_size < file_size and (float(file_size) / float(part_size)) <= num_parts


def calculate_etag(filepath: str):
    filesize = os.path.getsize(filepath)
    num_parts = 1
    part_sizes = [  # default part sizes
        AWS_CLI_BOTO3_PART_SIZE,  # aws_cli/boto3
        S3CMD_PART_SIZE,  # s3cmd
        factor_of_1MB(filesize, num_parts)  # Used by many clients to upload large files
    ]
    possible_sizes = list(filter(possible_part_sizes(filesize, num_parts), part_sizes)) or [filesize]
    result = [calc_etag(filepath, part_size) for part_size in possible_sizes]
    return result[0]


def file_etags(filepath: str, etag: str):
    etag = etag[1:-1]  # remove extra quotes
    filesize = os.path.getsize(filepath)
    num_parts = int(etag.split('-')[1])

    part_sizes = [  # default part sizes
        AWS_CLI_BOTO3_PART_SIZE,  # aws_cli/boto3
        S3CMD_PART_SIZE,  # s3cmd
        factor_of_1MB(filesize, num_parts)  # Used by many clients to upload large files
    ]

    possible_sizes = list(filter(possible_part_sizes(filesize, num_parts), part_sizes)) or [filesize]
    etags = [calc_etag(filepath, part_size) for part_size in possible_sizes]
    return "etag", etags


def file_etag(filepath: str, part_size: int = 0) -> tuple:
    """Calculate single part or multipart ETag for a file based on the part size.

    Single part ETag is just the MD5 hash of the file in hex format.
    No part number is appended to the ETag.(e.g. "4bb5142fc895507c983b4903016a7c11")

    Parameters
    ----------
    filepath : str
        The path to the file for which to calculate the ETag.
    part_size : int, optional
        The size of the parts for multipart ETags. If 0, a single-part ETag is calculated.

    Returns
    -------
    tuple
        A tuple containing the type ('etag') and the calculated ETag.
    """
    if part_size == 0:
        # If part size is 0 then calculate etag as single part
        return 'etag', f'\"{FileUtils.file_md5(f_name=filepath, b64=False)}\"'
    # return the multipart ETag
    return 'etag', f'\"{calc_etag(input_file=filepath, part_size=part_size)}\"'


def bytes_etags(file_bytes: bytes, etag: str):
    etag = etag[1:-1]  # remove extra quotes
    filesize = len(file_bytes)
    num_parts = int(etag.split('-')[1])

    part_sizes = [  # default part sizes
        AWS_CLI_BOTO3_PART_SIZE,  # aws_cli/boto3
        S3CMD_PART_SIZE,  # s3cmd
        factor_of_1MB(filesize, num_parts)  # Used by many clients to upload large files
    ]

    possible_sizes = list(filter(possible_part_sizes(filesize, num_parts), part_sizes)) or [filesize]
    etags = [calc_bytes_etag(file_bytes, part_size) for part_size in possible_sizes]
    return "etag", etags


def compare_etags(src_etag, dst_etags) -> bool:
    """Compares the source ETag with a list of destination ETags.

    Parameters
    ----------
    src_etag : tuple
        A tuple containing the type and value of the source ETag.
    dst_etags : tuple
        A tuple containing the type and a list of destination ETags.

    Returns
    -------
    bool
        True if the source ETag matches any of the destination ETags, False otherwise.
    """
    src_hash_type, src_hash_etag = src_etag
    dst_hash_type, dst_hash_etags = dst_etags
    if src_hash_type != dst_hash_type:
        return False
    src_hash_etag = src_hash_etag[1:-1]  # remove extra quotes
    for etag in dst_hash_etags:
        if etag == src_hash_etag:
            return True
    return False
