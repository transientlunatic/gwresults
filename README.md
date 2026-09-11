# gwresults

gwresults is a simple way to access parameter-estimation and
search results from LVK catalogue publications and third-party community
catalogues.

Posterior sample files are hosted on data repositories such as Zenodo,
alongside their catalogue publication, and can be large (multi-GB).
gwresults maintains a registry mapping event names to their Zenodo
record, downloads files on demand, and caches them locally. A bundled
table of summary statistics (median and highest-density interval per
parameter) lets you query across events without downloading anything.

## Install

```console
$ pip install gwresults
```

## Quickstart

### See what's bundled

The event registry ships with the package, so you can query it offline:

```console
$ gwresults list catalogues
GWTC-2.1
GWTC-3.0
GWTC-4.1
GWTC-5.0

$ gwresults list events --catalogue GWTC-2.1
GW150914_095045
GW151012_095443
...
```

### Fetch a posterior samples file

```console
$ gwresults get posterior --event GW150914_095045
/home/user/.cache/gwresults/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5
```

The short, date-only form (`GW150914`) also works if it's unambiguous.
The file is downloaded once and cached; later calls return the same path
without re-downloading. From Python:

```python
import gwresults

path = gwresults.posterior.get("GW150914_095045")
```

### Read posterior samples

A posterior file can hold more than one set of samples, one per waveform
approximant used in the analysis:

```python
from gwresults import io

analyses = io.list_analyses(path)
with io.open_posterior_samples(path, analyses[0]) as samples:
    total_mass = samples["total_mass"][:]
```

### Query across events by summary statistics

`gwresults.posterior.query` searches a bundled table of summary
statistics (median and highest-density interval per parameter) without
downloading any posterior files:

```python
import astropy.units as u
from gwresults.fields import total_mass, waveform_approximant

results = gwresults.posterior.query(
    total_mass >= 100 * u.solMass,
    waveform_approximant == "SEOBNRv5PHM",
)
```

> **Note:** the summary-statistics table ships empty until a maintainer
> populates it with `gwresults stats build` (see below), so `query()`
> currently returns no rows. The event registry above is unaffected —
> `get posterior` works today.

See the [quickstart tutorial](docs/tutorials/quickstart.rst) for more,
or the CLI's built-in help (`gwresults --help`).

## Maintainers

### Adding a catalogue to the registry

The event registry (mapping event name to Zenodo record and filename) is
generated from a catalogue's Zenodo record, not hand-written:

```console
$ gwresults registry generate --zenodo-record 6513631 --catalogue GWTC-2.1
Wrote 54 entries to .../data/registry/gwtc-2.1.yaml (54 total).
```

This queries the Zenodo API for the record's real file list and
checksums and derives each event's `gps_time` from its name, so nothing
is hand-typed. See
[`src/gwresults/data/registry/README.md`](src/gwresults/data/registry/README.md)
(or the "Maintaining the registry" tutorial in the docs) for the full
workflow, including disambiguating records that bundle multiple files
per event.

### Building the summary-statistics table

`gwresults.posterior.query` reads a bundled CSV built by
`gwresults stats build`. It downloads each event's (multi-GB) posterior
file in turn, extracts a handful of summary statistics from it, and
discards the file again — so running it across a whole catalogue takes a
long time and a lot of bandwidth:

```console
$ gwresults stats build --catalogue GWTC-2.1
Wrote 108 rows to .../data/summary_stats.csv (108 total).
```

Use `--event` (repeatable) to (re)build specific events instead of a
whole catalogue, and `--keep-cache` if you also want the downloaded
posterior files left in the local cache rather than deleted after use.
See the "Building the summary-statistics table" tutorial in the docs for
more.

## Status

The event registry is bundled for GWTC-2.1, GWTC-3.0, GWTC-4.1 and
GWTC-5.0 (`gwresults list catalogues` is the source of truth for what's
currently included) — `gwresults get posterior` works for any event in
them. The summary-statistics table is not yet populated (see above), and
search-pipeline results are planned but not yet implemented
(`gwresults.search`).

## Development

```console
$ pip install -e ".[test,docs]"
$ pytest
$ sphinx-build -b html docs docs/_build
```
