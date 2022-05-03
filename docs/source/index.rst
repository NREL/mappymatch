.. MapPyMatch documentation master file, created by
   sphinx-quickstart on Mon May  2 10:18:14 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MapPyMatch Documentation
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference/index

MapPyMatch is a pure-python package developed by the National Renewable Energy Laboratory that maintains a collection of map matching algorithms and wrappers. The package was designed for ease of use and portabilty across platforms.

TEST

Installation
------------

From PyPI
^^^^^^^^^

TODO

From Source (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^

First, clone the repository::

   git clone https://github.com/NREL/mappymatch.git && cd mappymatch

Then, setup a python environment with Python (at least version 3.8)::

   conda create -n mappymatch python=3.8

Finally, use pip to install the package::

   pip install -e .

.. warning::

   If you have issues installing the package and dependencies, you can try swapping step two above with the following command::

      conda env create -f environment.yml

Example Usage
-------------

Currently, ``osmnx`` is used to download a road network and match it using the ``LCSSMatcher``.

The ``LCSSMatcher`` implements the map matching algorithm described in `this <https://journals.sagepub.com/doi/10.3141/2645-08/>`_ paper.

.. code-block:: python

   from mappymatch import root
   from mappymatch.matchers.lcss.lcss import LCSSMatcher
   from mappymatch.utils.geo import geofence_from_trace
   from mappymatch.maps.nx.readers.osm_readers import read_osm_nxmap
   from mappymatch.constructs.trace import Trace

   trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")

   # generate a geofence polygon that surrounds the trace; units are in meters;
   # this is used to query OSM for a small map that we can match to
   geofence = geofence_from_trace(trace, padding=1e3)

   # uses osmnx to pull a networkx map from the OSM database
   road_map = read_osm_nxmap(geofence)

   matcher = LCSSMatcher(road_map)

   matches = matcher.match_trace(trace)

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`