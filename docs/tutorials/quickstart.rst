Quickstart
==========

Fetching a posterior
---------------------

Download (or locate the cached copy of) an event's posterior samples
file from the command line:

.. code-block:: console

   $ gwresults get posterior --event GW150914_095045
   /home/user/.cache/gwresults/GW150914_095045.h5

Or from Python:

.. code-block:: python

   import gwresults

   path = gwresults.posterior.get("GW150914_095045")

The file is downloaded once and cached; subsequent calls return the same
path without re-downloading.

Reading posterior samples
--------------------------

Posterior files can contain more than one set of samples, one per
waveform approximant used in the analysis. List what is available, and
select one with `gwresults.io.open_posterior_samples`:

.. code-block:: python

   from gwresults import io

   analyses = io.list_analyses(path)
   with io.open_posterior_samples(path, analyses[0]) as samples:
       total_mass = samples["total_mass"][:]

Querying across events
-----------------------

`gwresults.posterior.query` searches a bundled table of summary
statistics (median and highest-density interval per parameter) without
downloading any posterior files:

.. code-block:: python

   import astropy.units as u
   from gwresults import posterior
   from gwresults.fields import total_mass, waveform_approximant

   results = posterior.query(
       total_mass >= 100 * u.solMass,
       waveform_approximant == "SEOBNRv5PHM",
   )
