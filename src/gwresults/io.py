"""
Low-level HDF5 reading utilities for gravitational-wave posterior files.

These read the PE Data Release HDF5 format directly with `h5py`. This
deliberately avoids depending on `pesummary`: it is a much heavier
dependency and noticeably slower to open files with, and we only need a
small slice of what it offers.
"""

from __future__ import annotations

from contextlib import contextmanager

import h5py

_NON_ANALYSIS_KEYS = {"history", "version"}


def list_analyses(filename: str) -> list[str]:
    """
    List the analysis (waveform) groups available in a posterior file.

    Parameters
    ----------
    filename : str
        Path to a PE Data Release HDF5 file.

    Returns
    -------
    list of str
        Names of the analysis groups, e.g. ``["C01:Mixed", "C01:IMRPhenomXPHM"]``.
    """
    with h5py.File(filename, "r") as h5file:
        return [key for key in h5file if key not in _NON_ANALYSIS_KEYS]


@contextmanager
def open_posterior_samples(filename: str, analysis: str | None = None):
    """
    Open the posterior samples for a given analysis within a PE file.

    Parameters
    ----------
    filename : str
        Path to a PE Data Release HDF5 file.
    analysis : str, optional
        Name of the analysis group to read, e.g. ``"C01:IMRPhenomXPHM"``.
        If not given, the first available analysis is used.

    Yields
    ------
    h5py.Dataset
        The ``posterior_samples`` structured dataset for the chosen analysis.

    Raises
    ------
    ValueError
        If the requested analysis is not present in the file, or the file
        contains no analysis groups at all.

    Examples
    --------
    >>> with open_posterior_samples("GW150914.h5", "C01:Mixed") as samples:
    ...     total_mass = samples["total_mass"][:]
    """
    with h5py.File(filename, "r") as h5file:
        available = [key for key in h5file if key not in _NON_ANALYSIS_KEYS]
        if not available:
            raise ValueError(f"No analysis groups found in {filename}.")
        if analysis is None:
            analysis = available[0]
        elif analysis not in available:
            raise ValueError(
                f"Analysis '{analysis}' not found in {filename}. "
                f"Available analyses: {available}."
            )
        yield h5file[analysis]["posterior_samples"]
