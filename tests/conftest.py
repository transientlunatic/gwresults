"""Shared pytest fixtures for gwresults tests."""

from __future__ import annotations

import h5py
import numpy as np
import pytest
import yaml


@pytest.fixture
def registry_dir(tmp_path):
    """A directory containing a small, self-contained event registry."""
    entries = {
        "GW150914_095045": {
            "catalogue": "GWTC-1",
            "zenodo_record": 1234567,
            "filename": "GW150914_095045.h5",
            "gps_time": 1126259462.4,
        },
        "GW170817_120000": {
            "catalogue": "GWTC-1",
            "zenodo_record": 1234567,
            "filename": "GW170817_120000.h5",
            "gps_time": 1187008882.4,
        },
    }
    registry_file = tmp_path / "gwtc-1.yaml"
    registry_file.write_text(yaml.safe_dump(entries))
    return tmp_path


@pytest.fixture
def duplicate_registry_dir(tmp_path):
    """A registry directory with the same event defined in two files."""
    entry = {
        "GW150914_095045": {
            "catalogue": "GWTC-1",
            "zenodo_record": 1234567,
            "filename": "GW150914_095045.h5",
        }
    }
    (tmp_path / "a.yaml").write_text(yaml.safe_dump(entry))
    (tmp_path / "b.yaml").write_text(yaml.safe_dump(entry))
    return tmp_path


@pytest.fixture
def sample_posterior_file(tmp_path):
    """A small HDF5 file mimicking a PE Data Release with two analyses."""
    path = tmp_path / "GW150914_095045.h5"
    dtype = np.dtype([("total_mass", "f8"), ("chirp_mass", "f8")])

    with h5py.File(path, "w") as h5file:
        h5file.create_group("history")
        h5file.create_group("version")

        for analysis in ("C01:Mixed", "C01:IMRPhenomXPHM"):
            group = h5file.create_group(analysis)
            samples = np.zeros(1000, dtype=dtype)
            rng = np.random.default_rng(seed=1234)
            samples["total_mass"] = rng.normal(70, 5, size=1000)
            samples["chirp_mass"] = rng.normal(30, 2, size=1000)
            group.create_dataset("posterior_samples", data=samples)

    return path
