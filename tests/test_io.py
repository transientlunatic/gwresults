from __future__ import annotations

import pytest

from gwresults import io


def test_list_analyses_excludes_history_and_version(sample_posterior_file):
    analyses = io.list_analyses(sample_posterior_file)
    assert set(analyses) == {"C01:Mixed", "C01:IMRPhenomXPHM"}


def test_open_posterior_samples_defaults_to_first_analysis(sample_posterior_file):
    with io.open_posterior_samples(sample_posterior_file) as samples:
        assert "total_mass" in samples.dtype.names


def test_open_posterior_samples_selects_named_analysis(sample_posterior_file):
    with io.open_posterior_samples(sample_posterior_file, "C01:IMRPhenomXPHM") as samples:
        assert samples["total_mass"].shape == (1000,)


def test_open_posterior_samples_unknown_analysis_raises(sample_posterior_file):
    with pytest.raises(ValueError, match="not found"):
        with io.open_posterior_samples(sample_posterior_file, "does-not-exist"):
            pass


def test_open_posterior_samples_no_analyses_raises(tmp_path):
    import h5py

    path = tmp_path / "empty.h5"
    with h5py.File(path, "w") as h5file:
        h5file.create_group("history")
        h5file.create_group("version")

    with pytest.raises(ValueError, match="No analysis groups"):
        with io.open_posterior_samples(path):
            pass
