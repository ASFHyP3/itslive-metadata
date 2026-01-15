"""itslive-metadata processing."""

import logging
from pathlib import Path

from hyp3_itslive_metadata.cryoforge import generate_itslive_metadata, save_metadata


log = logging.getLogger(__name__)


def process_itslive_metadata(granule_uri: str) -> tuple[Path, Path, Path]:
    """Generates ITS_LIVE granule metadata files from a source S3 bucket and prefix.

    Args:
        granule_uri: URI to the granule or folder (s3://<bucket>/<prefix>) for the granule.

    Outputs:
        stac_item: local path to the generated STAC item.
        premet: local path to the generated NSIDC premet file.
        spatial: local path to the generated NSIDC spatial file.
    """
    log.info(f'Processing itslive metadata for granule: {granule_uri}')
    metadata = generate_itslive_metadata(
        url=granule_uri,
        store=None,  # Store is for Obstore
    )

    # saves the stac item and the NSIDC spatial+premet metadata files
    output_path = Path('./output')
    output_path.mkdir(parents=True, exist_ok=True)
    stac_item, premet, spatial, _ = save_metadata(metadata, './output')

    return Path(stac_item), Path(premet), Path(spatial)
