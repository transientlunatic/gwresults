"""Command line interface for gwresults."""

from __future__ import annotations

from pathlib import Path

import click

from . import posterior, registry_build
from .registry import RegistryError, _default_registry_dir


@click.group()
@click.version_option(package_name="gwresults")
def cli():
    """gwresults: access gravitational-wave parameter estimation results."""


@cli.group("get")
def get_group():
    """Download or locate a cached results file."""


@get_group.command("posterior")
@click.option(
    "--event",
    required=True,
    help="Event name, e.g. GW150914_095045, or the short form GW150914 if unambiguous.",
)
@click.option("--waveform", default=None, help="Waveform/analysis label to select.")
def get_posterior(event: str, waveform: str | None):
    """Download (or locate the cached copy of) a posterior samples file."""
    try:
        path = posterior.get(event, waveform=waveform)
    except (RegistryError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(path)


@cli.group("registry")
def registry_group():
    """Maintainer tools for building the event registry from Zenodo."""


@registry_group.command("generate")
@click.option("--zenodo-record", required=True, type=int, help="Zenodo record ID.")
@click.option("--catalogue", required=True, help="Catalogue name, e.g. GWTC-1.")
@click.option(
    "--pattern",
    default=registry_build.DEFAULT_EVENT_PATTERN,
    show_default=True,
    help="Regex (with one capture group) used to extract the event name "
    "from each filename in the record.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Registry YAML file to write/merge into. Defaults to the bundled "
    "registry directory, named after the catalogue.",
)
def registry_generate(zenodo_record: int, catalogue: str, pattern: str, output_path: Path | None):
    """Generate/update a catalogue's registry entries from its Zenodo record."""
    entries = registry_build.generate_entries(zenodo_record, catalogue, pattern)
    if not entries:
        raise click.ClickException(
            f"No files in Zenodo record {zenodo_record} matched pattern '{pattern}'."
        )

    if output_path is None:
        slug = catalogue.lower().replace(" ", "-")
        output_path = Path(_default_registry_dir()) / f"{slug}.yaml"

    merged = registry_build.merge_into_registry_file(entries, output_path)
    click.echo(f"Wrote {len(entries)} entries to {output_path} ({len(merged)} total).")


if __name__ == "__main__":  # pragma: no cover
    cli()
