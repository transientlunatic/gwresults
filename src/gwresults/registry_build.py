"""
Maintainer tooling for deterministically generating registry entries.

Given a Zenodo record ID, this queries the Zenodo API for the record's
actual file list and checksums, extracts each event name from its
filename, and derives `gps_time` from the event name itself (event names
encode a UTC timestamp). This avoids hand-typing `filename`/`hash` values
into the registry YAML files, which otherwise only surface a typo as a
download failure at `gwresults get` time.

Re-running this for a record is idempotent: entries it produces replace
any existing entries for the same event names, and other entries already
present in the file (e.g. from a different record) are left untouched.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import requests
import yaml
from astropy.time import Time

ZENODO_API_URL = "https://zenodo.org/api/records/{record_id}"
DEFAULT_EVENT_PATTERN = r"(GW\d{6}_\d{6})"
_EVENT_NAME_RE = re.compile(r"GW(\d{6})_(\d{6})")


def fetch_record_files(record_id: int | str) -> list[dict]:
    """
    Query the Zenodo API for a record's file list and checksums.

    Parameters
    ----------
    record_id : int or str
        Zenodo record ID.

    Returns
    -------
    list of dict
        One entry per file, each with (at least) ``key`` (filename) and
        ``checksum`` keys, as returned by the Zenodo API.

    Raises
    ------
    requests.HTTPError
        If the record cannot be retrieved.
    """
    response = requests.get(ZENODO_API_URL.format(record_id=record_id), timeout=30)
    response.raise_for_status()
    return response.json()["files"]


def extract_event_name(filename: str, pattern: str = DEFAULT_EVENT_PATTERN) -> str | None:
    """
    Extract an event name from a filename.

    Parameters
    ----------
    filename : str
        Filename to search.
    pattern : str, optional
        Regex used to find the event name. If it has a capture group,
        the first group is used as the event name; otherwise the whole
        match is used.

    Returns
    -------
    str or None
        The extracted event name, or None if the pattern did not match.
    """
    match = re.search(pattern, filename)
    if match is None:
        return None
    return match.group(1) if match.groups() else match.group(0)


def event_gps_time(event_name: str) -> float | None:
    """
    Derive the GPS time of an event from its name.

    Parameters
    ----------
    event_name : str
        Event name of the form ``GW<YYMMDD>_<HHMMSS>``, e.g.
        ``"GW150914_095045"``. The name encodes a UTC timestamp truncated
        to whole seconds, so the result may be up to ~1 second away from
        the event's true GPS time.

    Returns
    -------
    float or None
        GPS time in seconds, or None if ``event_name`` does not match the
        expected naming convention.
    """
    match = _EVENT_NAME_RE.fullmatch(event_name)
    if match is None:
        return None
    date_str, time_str = match.groups()
    timestamp = datetime.strptime(date_str + time_str, "%y%m%d%H%M%S")
    return float(Time(timestamp, scale="utc").gps)


def generate_entries(
    record_id: int | str,
    catalogue: str,
    pattern: str = DEFAULT_EVENT_PATTERN,
) -> dict:
    """
    Generate registry entries for every matching file in a Zenodo record.

    Parameters
    ----------
    record_id : int or str
        Zenodo record ID to query.
    catalogue : str
        Catalogue name to record against each entry, e.g. ``"GWTC-1"``.
    pattern : str, optional
        Regex used to extract the event name from each filename in the
        record. Files that don't match are skipped.

    Returns
    -------
    dict
        Mapping of event name to registry entry (``catalogue``,
        ``zenodo_record``, ``filename``, ``hash`` and, where derivable,
        ``gps_time``).

    Raises
    ------
    ValueError
        If more than one file in the record matches the same event name;
        the filename pattern needs to be narrowed to disambiguate.
    """
    entries: dict[str, dict] = {}
    matched_filenames: dict[str, str] = {}

    for file_info in fetch_record_files(record_id):
        filename = file_info["key"]
        event = extract_event_name(filename, pattern)
        if event is None:
            continue
        if event in entries:
            raise ValueError(
                f"Multiple files in record {record_id} match event '{event}' "
                f"({matched_filenames[event]!r} and {filename!r}); "
                "narrow --pattern to disambiguate."
            )

        entry = {
            "catalogue": catalogue,
            "zenodo_record": int(record_id),
            "filename": filename,
            "hash": file_info.get("checksum"),
        }
        gps_time = event_gps_time(event)
        if gps_time is not None:
            entry["gps_time"] = gps_time

        entries[event] = entry
        matched_filenames[event] = filename

    return entries


def merge_into_registry_file(entries: dict, path: Path) -> dict:
    """
    Merge generated entries into a registry YAML file, creating it if needed.

    Parameters
    ----------
    entries : dict
        Entries to merge in, as returned by `generate_entries`.
    path : pathlib.Path
        Registry YAML file to write/merge into.

    Returns
    -------
    dict
        The full merged set of entries now in the file.
    """
    existing = {}
    if path.exists():
        existing = yaml.safe_load(path.read_text()) or {}

    merged = {**existing, **entries}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(merged, sort_keys=True))
    return merged
