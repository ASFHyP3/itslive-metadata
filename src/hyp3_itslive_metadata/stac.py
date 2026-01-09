"""Helper functions for working with STAC catalogs."""

import json
import os
from pathlib import Path

import requests


def _get_stac_api_auth_headers() -> dict:
    try:
        stac_api_token = os.environ['STAC_API_TOKEN']
    except KeyError:
        raise ValueError('Please provide STAC item ingest credentials via the STAC_API_TOKEN environment variable.')

    return {'X-API-Key': stac_api_token}


def _ensure_items_endpoint(items_endpoint: str) -> str:
    items_endpoint = items_endpoint.rstrip('/')

    if not items_endpoint.endswith('/items'):
        raise ValueError(
            'Please provide a STAC item ingest endpoint, which will typically look like:\n'
            '   `https://<STAC_API>/collections/<COLLECTION>/items`\n'
            f'You provided: {items_endpoint}'
        )

    return items_endpoint


def update_stac_item_in_catalog(stac_item: Path | dict, items_endpoint: str) -> requests.Response:
    """Update STAC item already in a collection in a STAC catalog.

    Args:
        stac_item: The updated STAC item JSON.
        items_endpoint: URI to the STAC items endpoint for the STAC collection you want to add items to.

    Returns:
        The STAC catalog API response.

    Raises:
        requests.exceptions.HTTPError, if an HTTP error occurs.
    """
    if isinstance(stac_item, Path):
        stac_item: dict = json.loads(stac_item.read_text())

    items_endpoint = _ensure_items_endpoint(items_endpoint)
    url = f'{items_endpoint}/{stac_item["id"]}'
    headers = _get_stac_api_auth_headers()

    response = requests.put(url=url, headers=headers, json=stac_item)
    response.raise_for_status()

    return response


def add_stac_item_to_catalog(stac_item: Path | dict, items_endpoint: str) -> requests.Response:
    """Add STAC item to a collection in a STAC catalog.

    Args:
        stac_item: The new STAC item JSON.
        items_endpoint: URI to the STAC items endpoint for the STAC collection you want to add items to.

    Returns:
        The STAC catalog API response.

    Raises:
        requests.exceptions.HTTPError, if an HTTP error occurs.
    """
    if isinstance(stac_item, Path):
        stac_item: dict = json.loads(stac_item.read_text())

    items_endpoint = _ensure_items_endpoint(items_endpoint)
    headers = _get_stac_api_auth_headers()

    response = requests.post(url=items_endpoint, headers=headers, json=stac_item)
    response.raise_for_status()

    return response
