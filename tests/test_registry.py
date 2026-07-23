from __future__ import annotations

import pytest

from gwresults import registry


def test_load_registry_merges_files(registry_dir):
    entries = registry.load_registry(registry_dir)
    assert set(entries) == {"GW150914_095045", "GW170817_120000"}
    assert entries["GW150914_095045"]["catalogue"] == "GWTC-1"


def test_load_registry_duplicate_event_raises(duplicate_registry_dir):
    with pytest.raises(ValueError, match="Duplicate event"):
        registry.load_registry(duplicate_registry_dir)


def test_lookup_returns_entry(registry_dir):
    entry = registry.lookup("GW150914_095045", registry_dir)
    assert entry["filename"] == "GW150914_095045.h5"


def test_lookup_missing_event_raises(registry_dir):
    with pytest.raises(registry.RegistryError):
        registry.lookup("GW999999_000000", registry_dir)


def test_list_events_all(registry_dir):
    assert registry.list_events(directory=registry_dir) == [
        "GW150914_095045",
        "GW170817_120000",
    ]


def test_list_events_filtered_by_catalogue(registry_dir):
    assert registry.list_events(catalogue="GWTC-1", directory=registry_dir) == [
        "GW150914_095045",
        "GW170817_120000",
    ]
    assert registry.list_events(catalogue="GWTC-2", directory=registry_dir) == []


def test_load_registry_skips_non_yaml_files(registry_dir):
    (registry_dir / "README.md").write_text("not a registry file")
    entries = registry.load_registry(registry_dir)
    assert set(entries) == {"GW150914_095045", "GW170817_120000"}


def test_load_registry_defaults_to_bundled_registry():
    # No catalogue data is bundled yet, so this should be empty rather
    # than error, and it exercises the real default-directory lookup.
    entries = registry.load_registry()
    assert entries == {}
