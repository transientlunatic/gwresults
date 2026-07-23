from __future__ import annotations

import pytest

from gwresults import cache, registry


class _FakeFetcher:
    def __init__(self, path, base_url, registry):
        self.path = path
        self.base_url = base_url
        self.registry = registry

    def fetch(self, filename):
        return f"{self.path}/{filename}"


def test_fetch_builds_zenodo_doi_url_and_returns_cached_path(monkeypatch, registry_dir):
    monkeypatch.setattr(registry, "_default_registry_dir", lambda: registry_dir)
    captured = {}

    def fake_create(path, base_url, registry):
        captured["path"] = path
        captured["base_url"] = base_url
        captured["registry"] = registry
        return _FakeFetcher(path, base_url, registry)

    monkeypatch.setattr(cache.pooch, "create", fake_create)

    result = cache.fetch("GW150914_095045")

    assert captured["base_url"] == "doi:10.5281/zenodo.1234567"
    assert captured["registry"] == {"GW150914_095045.h5": None}
    assert result.endswith("GW150914_095045.h5")


def test_fetch_unknown_event_raises_registry_error(monkeypatch, registry_dir):
    monkeypatch.setattr(registry, "_default_registry_dir", lambda: registry_dir)
    with pytest.raises(registry.RegistryError):
        cache.fetch("GW000000_000000")
