"""
Summary statistics: median and highest-density intervals for posteriors.

The bundled summary-statistics table lets `gwresults.posterior.query` run
without downloading any of the (often multi-GB) posterior files.
"""

from __future__ import annotations

from importlib import resources

import numpy as np
import pandas as pd

DATA_PACKAGE = "gwresults.data"
SUMMARY_STATS_FILE = "summary_stats.csv"


def highest_density_interval(samples, credible_mass: float = 0.9) -> tuple[float, float]:
    """
    Compute the highest-density interval of a 1D sample set.

    Finds the narrowest interval containing ``credible_mass`` of the
    samples by sliding a fixed-mass window over the sorted samples.

    Parameters
    ----------
    samples : array_like
        1D array of posterior samples.
    credible_mass : float, optional
        Fraction of the posterior mass to enclose, by default 0.9.

    Returns
    -------
    tuple of float
        The ``(lower, upper)`` bounds of the interval.

    Raises
    ------
    ValueError
        If ``credible_mass`` is not strictly between 0 and 1, or if there
        are too few samples to form an interval.
    """
    if not 0 < credible_mass < 1:
        raise ValueError("credible_mass must be between 0 and 1.")

    sorted_samples = np.sort(np.asarray(samples))
    n_samples = len(sorted_samples)
    interval_size = int(np.floor(credible_mass * n_samples))

    if interval_size < 1 or interval_size >= n_samples:
        raise ValueError("Not enough samples to compute a credible interval.")

    n_candidates = n_samples - interval_size
    widths = sorted_samples[interval_size:] - sorted_samples[:n_candidates]
    min_index = int(np.argmin(widths))

    return float(sorted_samples[min_index]), float(sorted_samples[min_index + interval_size])


def summarise(samples, credible_mass: float = 0.9) -> dict:
    """
    Compute the median and highest-density interval of a 1D sample set.

    Parameters
    ----------
    samples : array_like
        1D array of posterior samples.
    credible_mass : float, optional
        Fraction of the posterior mass to enclose, by default 0.9.

    Returns
    -------
    dict
        Dictionary with keys ``median``, ``lower`` and ``upper``.
    """
    lower, upper = highest_density_interval(samples, credible_mass)
    return {"median": float(np.median(samples)), "lower": lower, "upper": upper}


def load_summary_table() -> pd.DataFrame:
    """
    Load the bundled summary-statistics table.

    Returns
    -------
    pandas.DataFrame
        One row per (event, waveform, parameter) combination, with
        ``median``, ``lower`` and ``upper`` columns.
    """
    table_path = resources.files(DATA_PACKAGE) / SUMMARY_STATS_FILE
    with resources.as_file(table_path) as path:
        return pd.read_csv(path)
