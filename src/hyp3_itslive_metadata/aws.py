"""Helper functions for working with AWS."""

import json
import logging
import os
from pathlib import Path

import boto3
import s3fs
from hyp3lib.aws import get_content_type, get_tag_set


def determine_granule_uri_from_bucket(bucket: str, prefix: str) -> str:
    """Find either a published netCDF velocity granule using the `publish_info.json` found in `s3://{bucket}/{prefix}`, or the first netCDF file found therein.

    Args:
        bucket: AWS S3 bucket to search in
        prefix: AWS s3 prefix within the bucket to search in

    Returns: S3 URI of the granule
    """
    s3_fs = s3fs.S3FileSystem(anon=False)

    granule_folder = f's3://{bucket}/{prefix}'
    logging.info(f'Looking for granule in {granule_folder}')
    if s3_fs.exists(f'{granule_folder}/publish_info.json'):
        publish_info = json.loads(s3_fs.cat(f'{granule_folder}/publish_info.json'))
        logging.debug(f'Found publish_info.json in {granule_folder}: {publish_info}')
        bucket = publish_info['bucket']
        prefix = publish_info['prefix']
        name = publish_info['name']
    else:
        granules = s3_fs.glob(f'{granule_folder}/*.nc')  # should only be one
        if not granules:
            raise ValueError(f'No granules found in {granule_folder}')
        name = Path(granules[0]).name

    return f's3://{bucket}/{prefix}/{name}'


def upload_file_to_s3_with_publish_access_keys(path_to_file: Path, bucket: str, prefix: str = '') -> None:
    """Upload a fail to `s3://{bucket}/{prefix}/` using AWS access keys found in the `PUBLISH_ACCESS_KEY_ID` and `PUBLISH_SECRET_ACCESS_KEY` environment variables.

    Args:
        path_to_file: Path to the file to upload
        bucket: AWS S3 bucket to upload files to
        prefix: AWS S3 prefix within the bucket to upload files to
    """
    try:
        access_key_id = os.environ['PUBLISH_ACCESS_KEY_ID']
        access_key_secret = os.environ['PUBLISH_SECRET_ACCESS_KEY']
    except KeyError:
        raise ValueError(
            'Please provide S3 Bucket upload access key credentials via the '
            'PUBLISH_ACCESS_KEY_ID and PUBLISH_SECRET_ACCESS_KEY environment variables'
        )

    s3_client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=access_key_secret)
    key = str(Path(prefix) / path_to_file.name)
    extra_args = {'ContentType': get_content_type(key)}

    logging.info(f'Uploading s3://{bucket}/{key}')
    s3_client.upload_file(str(path_to_file), bucket, key, extra_args)

    tag_set = get_tag_set(path_to_file.name)

    s3_client.put_object_tagging(Bucket=bucket, Key=key, Tagging=tag_set)
