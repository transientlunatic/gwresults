# Event registry

Each YAML file in this directory contributes entries to the merged event
registry (see `gwresults.registry`). We keep one file per catalogue
(e.g. `gwtc-1.yaml`, `gwtc-3.yaml`) so that adding a new catalogue is a
new file, not an edit to an existing one.

An event name must not appear in more than one file.

## Adding a catalogue

Don't hand-write these files. `gwresults registry generate` derives them
deterministically from the catalogue's Zenodo record: it queries the
Zenodo API for the actual file list and checksums, extracts each event
name from its filename, and derives `gps_time` from the event name
itself (event names encode a UTC timestamp).

```console
$ gwresults registry generate --zenodo-record 6513631 --catalogue GWTC-2.1
Wrote 54 entries to .../data/registry/gwtc-2.1.yaml (54 total).
```

Zenodo records typically bundle more than one file per event (e.g.
`_mixed_cosmo.h5` and `_mixed_nocosmo.h5` variants); the command raises
an error naming the ambiguous files rather than guessing, telling you to
narrow `--pattern` to disambiguate, e.g.:

```console
$ gwresults registry generate --zenodo-record 6513631 --catalogue GWTC-2.1 \
    --pattern '(GW\d{6}_\d{6})_PEDataRelease_mixed_cosmo\.h5'
```

Re-running the command for the same record is safe: its output entries
replace any existing entries for the same event names, and entries for
other events already in the file (e.g. from a different record) are left
untouched. Commit the generated YAML file — the PR diff is then
reproducible from the record ID alone, not hand-typed.

## Format

```yaml
GW150914_095045:
  catalogue: GWTC-1
  zenodo_record: 1234567    # numeric Zenodo record ID
  filename: GW150914_095045_PEDataRelease_mixed_cosmo.h5
  gps_time: 1126259462.0
  hash: md5:...             # enables download integrity verification
```

No catalogue data is bundled yet.
