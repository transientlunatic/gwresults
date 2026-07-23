# Event registry

Each YAML file in this directory contributes entries to the merged event
registry (see `gwresults.registry`). We keep one file per catalogue
(e.g. `gwtc-1.yaml`, `gwtc-3.yaml`) so that adding a new catalogue is a
new file, not an edit to an existing one.

An event name must not appear in more than one file.

## Format

```yaml
GW150914_095045:
  catalogue: GWTC-1
  zenodo_record: 1234567    # numeric Zenodo record ID
  filename: GW150914_095045_PEDataRelease_mixed_cosmo.h5
  gps_time: 1126259462.4
  hash: null                # optional: "md5:..." or "sha256:...", enables
                            # download integrity verification when set
```

`zenodo_record` and `filename` must be verified against the actual
Zenodo record for the catalogue's data release before being merged —
please double check these in review, since a wrong record/filename pair
will only surface as a download failure at `gwresults get` time.

No catalogue data is bundled yet. Add entries here via pull request.
