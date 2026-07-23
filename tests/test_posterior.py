from __future__ import annotations

import pandas as pd
import pytest

from gwresults import posterior
from gwresults.fields import total_mass, waveform_approximant


def test_get_returns_cached_path_without_waveform(monkeypatch, sample_posterior_file):
    monkeypatch.setattr(posterior.cache, "fetch", lambda event: str(sample_posterior_file))
    path = posterior.get("GW150914_095045")
    assert path == str(sample_posterior_file)


def test_get_validates_waveform(monkeypatch, sample_posterior_file):
    monkeypatch.setattr(posterior.cache, "fetch", lambda event: str(sample_posterior_file))
    path = posterior.get("GW150914_095045", waveform="C01:Mixed")
    assert path == str(sample_posterior_file)


def test_get_raises_for_unavailable_waveform(monkeypatch, sample_posterior_file):
    monkeypatch.setattr(posterior.cache, "fetch", lambda event: str(sample_posterior_file))
    with pytest.raises(ValueError, match="not available"):
        posterior.get("GW150914_095045", waveform="C01:DoesNotExist")


@pytest.fixture
def summary_table():
    return pd.DataFrame(
        {
            "event": ["GW150914_095045", "GW170817_120000", "GW190521_030229"],
            "total_mass": [65.0, 2.8, 150.0],
            "waveform_approximant": ["SEOBNRv5PHM", "IMRPhenomD", "SEOBNRv5PHM"],
        }
    )


def test_query_with_no_conditions_returns_full_table(monkeypatch, summary_table):
    monkeypatch.setattr(posterior.stats, "load_summary_table", lambda: summary_table)
    result = posterior.query()
    pd.testing.assert_frame_equal(result, summary_table)


def test_query_filters_on_single_condition(monkeypatch, summary_table):
    monkeypatch.setattr(posterior.stats, "load_summary_table", lambda: summary_table)
    result = posterior.query(total_mass >= 100)
    assert result["event"].tolist() == ["GW190521_030229"]


def test_query_combines_multiple_conditions_with_and(monkeypatch, summary_table):
    monkeypatch.setattr(posterior.stats, "load_summary_table", lambda: summary_table)
    result = posterior.query(total_mass >= 50, waveform_approximant == "SEOBNRv5PHM")
    assert result["event"].tolist() == ["GW150914_095045", "GW190521_030229"]
