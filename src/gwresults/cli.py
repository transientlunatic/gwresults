"""Command line interface for gwresults."""

from __future__ import annotations

import click

from . import posterior
from .registry import RegistryError


@click.group()
@click.version_option(package_name="gwresults")
def cli():
    """gwresults: access gravitational-wave parameter estimation results."""


@cli.group("get")
def get_group():
    """Download or locate a cached results file."""


@get_group.command("posterior")
@click.option("--event", required=True, help="Event name, e.g. GW150914_095045.")
@click.option("--waveform", default=None, help="Waveform/analysis label to select.")
def get_posterior(event: str, waveform: str | None):
    """Download (or locate the cached copy of) a posterior samples file."""
    try:
        path = posterior.get(event, waveform=waveform)
    except (RegistryError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(path)


if __name__ == "__main__":  # pragma: no cover
    cli()
