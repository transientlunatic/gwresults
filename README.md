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
$ pip install -e ".[test,docs]"
```

## Usage

Command line:

```console
$ gwresults get posterior --event GW150914_095045
```

Python:

```python
import gwresults

path = gwresults.posterior.get("GW150914_095045")
```

Querying across events by summary statistics:

```python
import astropy.units as u
from gwresults.fields import total_mass, waveform_approximant

results = gwresults.posterior.query(
    total_mass >= 100 * u.solMass,
    waveform_approximant == "SEOBNRv5PHM",
)
```

## Adding events (maintainers)

No catalogue data is bundled yet. Events are added by generating a
registry file from its Zenodo record, not by hand-writing one:

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

## Status

Early scaffold. Currently supports published parameter-estimation
posteriors only; search-pipeline results are planned but not yet
implemented (`gwresults.search`).

## Development

```console
$ pip install -e ".[test,docs]"
$ pytest
$ sphinx-build -b html docs docs/_build
```
