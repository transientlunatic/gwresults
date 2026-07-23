Maintaining the registry
=========================

The event registry (see :doc:`../api`, `gwresults.registry`) maps event
names to the Zenodo record and filename that holds their posterior
samples. No catalogue data is bundled with gwresults yet — this
tutorial walks through adding one.

Don't hand-write the registry YAML files in
``src/gwresults/data/registry/``. Instead, use
``gwresults registry generate``, which derives them deterministically
from the catalogue's Zenodo record: it queries the Zenodo API for the
record's actual file list and checksums, extracts each event name from
its filename, and derives ``gps_time`` from the event name itself (event
names encode a UTC timestamp). Hand-typed ``filename``/``hash`` values
would only surface a typo as a download failure at ``gwresults get``
time; this way there's nothing to typo.

Basic usage
-----------

.. code-block:: console

   $ gwresults registry generate --zenodo-record 6513631 --catalogue GWTC-2.1
   Wrote 54 entries to .../data/registry/gwtc-2.1.yaml (54 total).

This writes (or updates) ``gwtc-2.1.yaml`` in the bundled registry
directory, named after the catalogue.

Disambiguating filenames
-------------------------

Zenodo records often bundle more than one file per event — for example
``_mixed_cosmo.h5`` and ``_mixed_nocosmo.h5`` variants. When more than
one file in the record matches the same event name, the command refuses
to guess and instead reports the conflicting files:

.. code-block:: console

   $ gwresults registry generate --zenodo-record 6513631 --catalogue GWTC-2.1
   Error: Multiple files in record 6513631 match event 'GW190707_093326'
   ('IGWN-GWTC2p1-v2-GW190707_093326_PEDataRelease_mixed_cosmo.h5' and
   'IGWN-GWTC2p1-v2-GW190707_093326_PEDataRelease_mixed_nocosmo.h5');
   narrow --pattern to disambiguate.

Narrow ``--pattern`` (a regex with one capture group for the event name)
to select the variant you want:

.. code-block:: console

   $ gwresults registry generate --zenodo-record 6513631 --catalogue GWTC-2.1 \
       --pattern '(GW\d{6}_\d{6})_PEDataRelease_mixed_cosmo\.h5'
   Wrote 54 entries to .../data/registry/gwtc-2.1.yaml (54 total).

Re-running and updating
-------------------------

Re-running the command for the same record is safe: the entries it
produces replace any existing entries for the same event names, while
entries for other events already in the file (e.g. added from a
different record) are left untouched. This makes it idempotent — running
it again after Zenodo updates a record's checksums, for instance, simply
refreshes those entries.

Once generated, commit the YAML file via pull request. Since it's
derived entirely from the Zenodo record ID, the diff is reproducible by
anyone re-running the same command, rather than a hand-typed value that
can only be checked by someone re-downloading the file.

See the :doc:`../api` reference for `gwresults.registry_build` for the
full set of functions this command is built from, if you need to script
something more custom (e.g. generating several catalogues in one pass).
