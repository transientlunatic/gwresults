from __future__ import annotations

import pytest
import yaml

from gwresults import registry_build


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_extract_event_name_default_pattern():
    filename = "IGWN-GWTC2p1-v2-GW190814_211039_PEDataRelease_mixed_cosmo.h5"
    assert registry_build.extract_event_name(filename) == "GW190814_211039"


def test_extract_event_name_no_match_returns_none():
    assert registry_build.extract_event_name("README.md") is None


def test_extract_event_name_pattern_without_capture_group():
    assert registry_build.extract_event_name("event.h5", pattern=r"event") == "event"


def test_event_gps_time_matches_known_value():
    gps = registry_build.event_gps_time("GW150914_095045")
    assert gps == pytest.approx(1126259462, abs=1)
    assert type(gps) is float  # noqa: E721 -- must be YAML-serialisable, not numpy.float64


def test_event_gps_time_returns_none_for_non_matching_name():
    assert registry_build.event_gps_time("not-an-event") is None


def test_fetch_record_files_calls_zenodo_api(monkeypatch):
    captured = {}

    def fake_get(url, timeout):
        captured["url"] = url
        captured["timeout"] = timeout
        return _FakeResponse({"files": [{"key": "a.h5", "checksum": "md5:abc"}]})

    monkeypatch.setattr(registry_build.requests, "get", fake_get)
    files = registry_build.fetch_record_files(1234567)

    assert captured["url"] == "https://zenodo.org/api/records/1234567"
    assert files == [{"key": "a.h5", "checksum": "md5:abc"}]


def test_generate_entries_builds_expected_entries(monkeypatch):
    files = [
        {"key": "GW150914_095045_PEDataRelease_mixed_cosmo.h5", "checksum": "md5:aaa"},
        {"key": "GW170817_120000_PEDataRelease_mixed_cosmo.h5", "checksum": "md5:bbb"},
        {"key": "README.md", "checksum": "md5:ccc"},
    ]
    monkeypatch.setattr(registry_build, "fetch_record_files", lambda record_id: files)

    entries = registry_build.generate_entries(1234567, "GWTC-1")

    assert set(entries) == {"GW150914_095045", "GW170817_120000"}
    assert entries["GW150914_095045"] == {
        "catalogue": "GWTC-1",
        "zenodo_record": 1234567,
        "filename": "GW150914_095045_PEDataRelease_mixed_cosmo.h5",
        "hash": "md5:aaa",
        "gps_time": pytest.approx(1126259462, abs=1),
    }


def test_generate_entries_raises_on_ambiguous_match(monkeypatch):
    files = [
        {"key": "GW150914_095045_mixed_cosmo.h5", "checksum": "md5:aaa"},
        {"key": "GW150914_095045_mixed_nocosmo.h5", "checksum": "md5:bbb"},
    ]
    monkeypatch.setattr(registry_build, "fetch_record_files", lambda record_id: files)

    with pytest.raises(ValueError, match="Multiple files"):
        registry_build.generate_entries(1234567, "GWTC-1")


def test_generate_entries_output_is_yaml_serialisable(monkeypatch, tmp_path):
    files = [{"key": "GW150914_095045_PEDataRelease_mixed_cosmo.h5", "checksum": "md5:aaa"}]
    monkeypatch.setattr(registry_build, "fetch_record_files", lambda record_id: files)

    entries = registry_build.generate_entries(1234567, "GWTC-1")
    # yaml.safe_dump raises RepresenterError on non-native types (e.g. numpy
    # floats from astropy), which round-tripping through a real file catches.
    registry_build.merge_into_registry_file(entries, tmp_path / "gwtc-1.yaml")


def test_merge_into_registry_file_creates_new_file(tmp_path):
    entries = {"GW150914_095045": {"catalogue": "GWTC-1", "filename": "a.h5"}}
    path = tmp_path / "gwtc-1.yaml"

    merged = registry_build.merge_into_registry_file(entries, path)

    assert merged == entries
    assert yaml.safe_load(path.read_text()) == entries


def test_merge_into_registry_file_preserves_other_entries(tmp_path):
    path = tmp_path / "gwtc-1.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "GW150914_095045": {"catalogue": "GWTC-1", "filename": "old.h5"},
                "GW151226_033853": {"catalogue": "GWTC-1", "filename": "other.h5"},
            }
        )
    )

    new_entries = {"GW150914_095045": {"catalogue": "GWTC-1", "filename": "new.h5"}}
    merged = registry_build.merge_into_registry_file(new_entries, path)

    assert merged["GW150914_095045"]["filename"] == "new.h5"
    assert merged["GW151226_033853"]["filename"] == "other.h5"
    assert yaml.safe_load(path.read_text()) == merged
