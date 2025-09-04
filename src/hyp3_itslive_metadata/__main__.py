"""itslive-metadata processing for HyP3."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urlparse

from hyp3lib.aws import upload_file_to_s3

from hyp3_itslive_metadata.aws import determine_granule_uri_from_bucket, upload_file_to_s3_with_publish_access_keys
from hyp3_itslive_metadata.process import process_itslive_metadata


def _str_without_trailing_slash(s: str) -> str:
    return s.rstrip('/')


def _nullable_string(argument_string: str) -> str | None:
    argument_string = argument_string.replace('None', '').strip()
    return argument_string if argument_string else None


def main() -> None:
    """HyP3 entrypoint for hyp3_itslive_metadata."""
    parser = ArgumentParser()
    hyp3_group = parser.add_argument_group(
        'HyP3 content bucket',
        'AWS S3 bucket and prefix to upload metadata product(s) to. Will also be used to find the input granule if `--granule-uri` is not provided`.',
    )
    hyp3_group.add_argument('--bucket')
    hyp3_group.add_argument('--bucket-prefix', default='')

    parser.add_argument(
        '--granule-uri',
        help='URI for a granule to generate metadata for. If not provided, will find the first granule in HyP3 content bucket.',
    )

    publish_group = parser.add_argument_group(
        'Data publishing bucket', 'AWS S3 bucket and prefix to publish STAC JSONs to.'
    )
    publish_group.add_argument(
        '--publish-bucket',
        type=_nullable_string,
    )
    publish_group.add_argument(
        '--publish-prefix',
        type=_str_without_trailing_slash,
    )
    args = parser.parse_args()

    if args.granule_uri is None:
        if args.bucket:
            args.granule_uri = determine_granule_uri_from_bucket(args.bucket, args.bucket_prefix)
        else:
            raise ValueError('Must provide --granule-uri or --bucket')

    if args.publish_bucket and not args.publish_prefix:
        raise ValueError('If you provide --publish-bucket you mist also provide --publish-prefix')

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
    )
    logging.info(f'Processing itslive metadata with args: {args}')

    metadata_files = process_itslive_metadata(args.granule_uri)

    if args.bucket and args.bucket_prefix:
        logging.info(f'Uploading metadata files to s3://{args.bucket}/{args.bucket_prefix}/')
        for file in metadata_files:
            upload_file_to_s3(file, args.bucket, args.bucket_prefix)

    if args.publish_bucket:
        for file in metadata_files:
            if '.stac.json' in file.name:
                logging.info(f'Publishing STAC JSON to: s3://{args.publish_bucket}/{args.publish_prefix}/{file.name}')
                upload_file_to_s3_with_publish_access_keys(file, bucket=args.publish_bucket, prefix=args.publish_prefix)
            else:
                granule_prefix = str(Path(urlparse(args.granule_uri).path).parent).lstrip('/')
                logging.info(f'Publishing {file.suffix} to: s3://{args.publish_bucket}/{granule_prefix}/{file.name}')
                upload_file_to_s3_with_publish_access_keys(file, bucket=args.publish_bucket, prefix=granule_prefix)


if __name__ == '__main__':
    main()
