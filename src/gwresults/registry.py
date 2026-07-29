"""
Event registry: mapping between event names and their Zenodo data locations.

The registry is a set of bundled YAML files (one per catalogue), each
mapping an event name to the Zenodo record and filename that holds its
posterior samples. New events are added by editing or adding a YAML file
in ``gwresults/data/registry`` and opening a pull request.
"""

from __future__ import annotations

import re
from importlib import resources
from pathlib import Path

import yaml

DATA_PACKAGE = "gwresults.data"
REGISTRY_SUBDIR = "registry"
_SHORT_NAME_RE = re.compile(r"GW\d{6}")


class RegistryError(KeyError):
    """Raised when an event cannot be found in the registry."""


def _default_registry_dir() -> Path:
    return resources.files(DATA_PACKAGE) / REGISTRY_SUBDIR


def load_registry(directory: Path | None = None) -> dict:
    """
    Load and merge all catalogue registry files in a directory.

    Parameters
    ----------
    directory : pathlib.Path, optional
        Directory containing registry YAML files. Defaults to the
        registry bundled with the package.

    Returns
    -------
    dict
        Mapping of event name to its registry entry, e.g. ``catalogue``,
        ``zenodo_record`` and ``filename``.

    Raises
    ------
    ValueError
        If the same event name appears in more than one registry file.
    """
    if directory is None:
        directory = _default_registry_dir()

    merged: dict[str, dict] = {}
    for registry_file in sorted(Path(directory).iterdir()):
        if registry_file.suffix not in (".yaml", ".yml"):
            continue
        entries = yaml.safe_load(registry_file.read_text()) or {}
        for name, entry in entries.items():
            if name in merged:
                raise ValueError(
                    f"Duplicate event '{name}' found in {registry_file.name}."
                )
            merged[name] = dict(entry)

    return merged


def lookup(event: str, directory: Path | None = None) -> dict:
    """
    Look up the registry entry for a single event.

    Parameters
    ----------
    event : str
        Event name, either the full form (e.g. ``"GW150914_095045"``) or
        the short, date-only form (e.g. ``"GW150914"``). The short form
        resolves to the matching full name if exactly one registry entry
        shares that date.
    directory : pathlib.Path, optional
        Directory containing registry YAML files. Defaults to the
        registry bundled with the package.

    Returns
    -------
    dict
        Registry entry with keys such as ``catalogue``, ``zenodo_record``
        and ``filename``.

    Raises
    ------
    RegistryError
        If the event is not present in any registry file, or if a short
        name matches more than one entry.
    """
    entries = load_registry(directory)
    if event in entries:
        return entries[event]

    if _SHORT_NAME_RE.fullmatch(event):
        matches = sorted(name for name in entries if name.startswith(f"{event}_"))
        if len(matches) == 1:
            return entries[matches[0]]
        if len(matches) > 1:
            raise RegistryError(
                f"Event name '{event}' is ambiguous; matches {matches}. "
                "Use the full name to disambiguate."
            )

    raise RegistryError(f"No registry entry found for event '{event}'.")


def list_events(catalogue: str | None = None, directory: Path | None = None) -> list[str]:
    """
    List all event names in the registry.

    Parameters
    ----------
    catalogue : str, optional
        If given, restrict the list to events from a single catalogue.
    directory : pathlib.Path, optional
        Directory containing registry YAML files. Defaults to the
        registry bundled with the package.

    Returns
    -------
    list of str
        Sorted event names.
    """
    entries = load_registry(directory)
    if catalogue is None:
        return sorted(entries)
    return sorted(
        name for name, entry in entries.items() if entry.get("catalogue") == catalogue
    )
