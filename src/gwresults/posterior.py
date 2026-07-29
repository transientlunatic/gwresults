"""Public interface for accessing posterior samples."""

from __future__ import annotations

import pandas as pd

from . import cache, io, stats
from .fields import CompoundCondition, Condition


def get(event: str, waveform: str | None = None) -> str:
    """
    Get the path to the (downloaded and cached) posterior file for an event.

    Parameters
    ----------
    event : str
        Event name, either the full form (e.g. ``"GW150914_095045"``) or
        the short, date-only form (e.g. ``"GW150914"``) if unambiguous.
    waveform : str, optional
        Name of the waveform/analysis group to select, e.g.
        ``"C01:IMRPhenomXPHM"``. If not given, the file is returned as-is
        and the caller is responsible for choosing an analysis group.

    Returns
    -------
    str
        Path to the cached posterior HDF5 file.

    Raises
    ------
    gwresults.registry.RegistryError
        If the event is not present in the bundled registry.
    ValueError
        If ``waveform`` is given but not available in the posterior file.
    """
    path = cache.fetch(event)
    if waveform is not None and waveform not in io.list_analyses(path):
        raise ValueError(f"Waveform '{waveform}' not available for {event}.")
    return path


def query(*conditions: Condition | CompoundCondition) -> pd.DataFrame:
    """
    Query the bundled summary-statistics table.

    Parameters
    ----------
    *conditions
        Conditions built from `gwresults.fields`, e.g.
        ``total_mass >= 100 * u.solMass``. Multiple conditions are
        combined with a logical AND.

    Returns
    -------
    pandas.DataFrame
        Rows of the summary-statistics table matching all conditions.

    Examples
    --------
    >>> from gwresults.fields import total_mass, waveform_approximant
    >>> import astropy.units as u
    >>> query(total_mass >= 100 * u.solMass, waveform_approximant == "SEOBNRv5PHM")
    """
    table = stats.load_summary_table()
    if not conditions:
        return table
    mask = conditions[0].evaluate(table)
    for condition in conditions[1:]:
        mask &= condition.evaluate(table)
    return table[mask]
