Examples 
================ 

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