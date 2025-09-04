"""itslive-metadata processing."""

import logging
from pathlib import Path

from cryoforge import generate_itslive_metadata, save_metadata


log = logging.getLogger(__name__)


def process_itslive_metadata(granule_uri: str) -> list[Path]:
    """Generates ITS_LIVE granule metadata files from a source S3 bucket and prefix.

    Args:
        granule_uri: URI to the granule or folder (s3://<bucket>/<prefix>) for the granule.

    Outputs:
        str: S3 path of the generated STAC item.
    """
    log.info(f'Processing itslive metadata for granule: {granule_uri}')
    metadata = generate_itslive_metadata(
        url=granule_uri,
        store=None,  # Store is for Obstore
    )

    # saves the stac item and the NSIDC spatial+premet metadata files
    output_path = Path('./output')
    output_path.mkdir(parents=True, exist_ok=True)
    save_metadata(metadata, './output')
    file_paths = [f for f in Path('./output').glob('*') if not f.name.endswith('.ref.json')]

    return file_paths
