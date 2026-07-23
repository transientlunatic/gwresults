"""
Downloading and caching of posterior data files from Zenodo.

Files are fetched with `pooch`, which stores them in an OS-appropriate
cache directory and verifies them by hash on subsequent calls, so a
second request for the same event returns the cached path without
re-downloading.
"""

from __future__ import annotations

import pooch

from . import registry

CACHE_DIR = pooch.os_cache("gwresults")


def _zenodo_url(zenodo_record: int | str) -> str:
    return f"doi:10.5281/zenodo.{zenodo_record}"


def fetch(event: str) -> str:
    """
    Get the local path to the posterior file for an event, downloading it
    if it is not already cached.

    Parameters
    ----------
    event : str
        Event name, e.g. ``"GW150914_095045"``.

    Returns
    -------
    str
        Path to the cached posterior HDF5 file.

    Raises
    ------
    gwresults.registry.RegistryError
        If the event is not present in the bundled registry.
    """
    entry = registry.lookup(event)
    fetcher = pooch.create(
        path=CACHE_DIR,
        base_url=_zenodo_url(entry["zenodo_record"]),
        registry={entry["filename"]: entry.get("hash")},
    )
    return fetcher.fetch(entry["filename"])
