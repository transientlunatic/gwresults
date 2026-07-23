from __future__ import annotations

from click.testing import CliRunner

from gwresults import cli, posterior
from gwresults.registry import RegistryError


def test_get_posterior_command_echoes_path(monkeypatch):
    monkeypatch.setattr(posterior, "get", lambda event, waveform=None: "/cache/path.h5")
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["get", "posterior", "--event", "GW150914_095045"])
    assert result.exit_code == 0
    assert result.output.strip() == "/cache/path.h5"


def test_get_posterior_command_passes_waveform(monkeypatch):
    captured = {}

    def fake_get(event, waveform=None):
        captured["event"] = event
        captured["waveform"] = waveform
        return "/cache/path.h5"

    monkeypatch.setattr(posterior, "get", fake_get)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "get",
            "posterior",
            "--event",
            "GW150914_095045",
            "--waveform",
            "C01:Mixed",
        ],
    )
    assert result.exit_code == 0
    assert captured == {"event": "GW150914_095045", "waveform": "C01:Mixed"}


def test_get_posterior_requires_event_option():
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["get", "posterior"])
    assert result.exit_code != 0


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["--help"])
    assert result.exit_code == 0


def test_get_posterior_reports_unknown_event_cleanly(monkeypatch):
    def fake_get(event, waveform=None):
        raise RegistryError(f"No registry entry found for event '{event}'.")

    monkeypatch.setattr(posterior, "get", fake_get)
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["get", "posterior", "--event", "GW000000_000000"])
    assert result.exit_code != 0
    assert "No registry entry found" in result.output
    assert "Traceback" not in result.output


def test_get_posterior_reports_bad_waveform_cleanly(monkeypatch):
    def fake_get(event, waveform=None):
        raise ValueError(f"Waveform '{waveform}' not available for {event}.")

    monkeypatch.setattr(posterior, "get", fake_get)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        ["get", "posterior", "--event", "GW150914_095045", "--waveform", "bogus"],
    )
    assert result.exit_code != 0
    assert "not available" in result.output
    assert "Traceback" not in result.output
