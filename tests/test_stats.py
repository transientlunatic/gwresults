from __future__ import annotations

import numpy as np
import pytest

from gwresults import stats


def test_highest_density_interval_on_uniform_samples():
    rng = np.random.default_rng(seed=42)
    samples = rng.uniform(0, 10, size=100_000)
    lower, upper = stats.highest_density_interval(samples, credible_mass=0.5)
    assert upper - lower == pytest.approx(5.0, abs=0.1)


def test_highest_density_interval_invalid_credible_mass():
    with pytest.raises(ValueError, match="credible_mass"):
        stats.highest_density_interval([1, 2, 3], credible_mass=1.5)


def test_highest_density_interval_too_few_samples():
    with pytest.raises(ValueError, match="Not enough samples"):
        stats.highest_density_interval([1], credible_mass=0.9)


def test_summarise_returns_expected_keys():
    rng = np.random.default_rng(seed=7)
    samples = rng.normal(70, 5, size=10_000)
    result = stats.summarise(samples)
    assert set(result) == {"median", "lower", "upper"}
    assert result["median"] == pytest.approx(70, abs=1)
    assert result["lower"] < result["median"] < result["upper"]


def test_load_summary_table_has_expected_columns():
    table = stats.load_summary_table()
    assert "event" in table.columns
    assert "total_mass" in table.columns
    assert "waveform_approximant" in table.columns
