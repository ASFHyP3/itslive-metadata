"""itslive-metadata processing for HyP3."""

import argparse
import json
import logging
import sys
from importlib.metadata import entry_points
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from hyp3lib.aws import upload_file_to_s3
from tqdm.auto import tqdm

from hyp3_itslive_metadata.aws import determine_granule_uri_from_bucket, upload_file_to_s3_with_publish_access_keys
from hyp3_itslive_metadata.process import process_itslive_metadata


tqdm.pandas()


def _hyp3_upload_and_publish(
    metadata_files: list[Path],
    *,
    bucket: str | None = None,
    bucket_prefix: str = '',
    publish_bucket: str | None = None,
    publish_prefix: str = '',
) -> None:
    if bucket and bucket_prefix:
        logging.info(f'Uploading metadata files to s3://{bucket}/{bucket_prefix}/')
        for file in metadata_files:
            upload_file_to_s3(file, bucket, bucket_prefix)

    if publish_bucket:
        logging.info(f'Publishing metadata files to s3://{publish_bucket}/{publish_prefix}')
        for file in metadata_files:
            upload_file_to_s3_with_publish_access_keys(file, bucket=publish_bucket, prefix=publish_prefix)


def _str_without_trailing_slash(s: str) -> str:
    return s.rstrip('/')


def _nullable_string(argument_string: str) -> str | None:
    argument_string = argument_string.replace('None', '').strip()
    return argument_string if argument_string else None


def _nullable_int(argument_string: str) -> int | None:
    argument_string = argument_string.replace('None', '').strip()
    return int(argument_string) if argument_string else None


def hyp3_meta() -> None:
    """HyP3 entrypoint for hyp3_itslive_metadata."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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

    parser.add_argument(
        '--publish-bucket',
        type=_nullable_string,
        default=None,
        help='Additionally, publish products to this bucket. Necessary credentials must be provided '
        'via the `PUBLISH_ACCESS_KEY_ID` and `PUBLISH_SECRET_ACCESS_KEY` environment variables.',
    )

    args = parser.parse_args()

    if args.granule_uri is None:
        if args.bucket:
            args.granule_uri = determine_granule_uri_from_bucket(args.bucket, args.bucket_prefix)
        else:
            raise ValueError('Must provide --granule-uri or --bucket')

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
    )
    logging.info(f'Processing itslive metadata with args: {args}')

    metadata_files = process_itslive_metadata(args.granule_uri)
    publish_prefix = str(Path(urlparse(args.granule_uri).path).parent).lstrip('/')
    _hyp3_upload_and_publish(
        metadata_files,
        bucket=args.publish_bucket,
        bucket_prefix=args.bucket_prefix,
        publish_bucket=args.publish_bucket,
        publish_prefix=publish_prefix,
    )


def hyp3_bulk_meta() -> None:
    """HyP3 entrypoint for bulk running hyp3_itslive_metadata."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    hyp3_group = parser.add_argument_group(
        'HyP3 content bucket',
        'AWS S3 bucket and prefix to upload metadata product(s) to.',
    )
    hyp3_group.add_argument('--bucket')
    hyp3_group.add_argument('--bucket-prefix', default='')

    parser.add_argument(
        '--granules-parquet',
        default='s3://its-live-data/test-space/stac/granules_to_recrop.parquet',
        help='URI to a parquet file containing granule URIs to generate metadata for',
    )

    parser.add_argument(
        '--start-idx', type=_nullable_int, default=0, help='Start index of the granules to generate metadata for.'
    )
    parser.add_argument(
        '--stop-idx', type=_nullable_int, default=None, help='Stop index of the granules to generate metadata for.'
    )

    parser.add_argument(
        '--publish-bucket',
        type=_nullable_string,
        default=None,
        help='Additionally, publish products to this bucket. Necessary credentials must be provided '
        'via the `PUBLISH_ACCESS_KEY_ID` and `PUBLISH_SECRET_ACCESS_KEY` environment variables.',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
    )
    logging.info(f'Processing bulk itslive metadata with args: {args}')

    df = pd.read_parquet(args.granules_parquet, engine='pyarrow')

    stac_paths = []
    for granule_bucket, granule_key in tqdm(
        df.loc[args.start_idx : args.stop_idx, ['bucket', 'key']].itertuples(index=False), initial=args.start_idx
    ):
        metadata_files = process_itslive_metadata(f's3://{granule_bucket}/{granule_key}')
        stac_paths.append(metadata_files[0])
        _hyp3_upload_and_publish(
            metadata_files, publish_bucket=args.publish_bucket, publish_prefix=str(Path(granule_key).parent)
        )

    stac_ndjson = Path.cwd() / f'{Path(args.granule_parquet).stem}_{args.start_idx}-{args.stop_idx}.ndjson'
    logging.info(f'Combining all {len(stac_paths)} STAC items into {stac_ndjson} for ingest')

    stac_items = []
    for stac_path in tqdm(stac_paths):
        stac_items.append(json.dumps(json.loads(stac_path.read_text())))  # roundtrip to ensure no newlines

    stac_ndjson.write_text('\n'.join(stac_items))
    _hyp3_upload_and_publish([stac_ndjson], bucket=args.bucket, bucket_prefix=args.bucket_prefix)


def main() -> None:
    """Main entrypoint for HyP3."""
    parser = argparse.ArgumentParser(prefix_chars='+', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '++process',
        choices=['meta', 'bulk_meta'],
        default='meta',
        help='Select the hyp3-plugin entrypoint to use',  # as specified in `pyproject.toml`
    )
    parser.add_argument('++omp-num-threads', type=int, help='The number of OpenMP threads to use for parallel regions')

    args, unknowns = parser.parse_known_args()

    discovered_plugins = entry_points(group='hyp3.plugins')

    sys.argv = [args.process, *unknowns]
    sys.exit(discovered_plugins[args.process].load()())


if __name__ == '__main__':
    main()
