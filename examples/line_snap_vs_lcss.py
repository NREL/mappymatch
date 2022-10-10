from pathlib import Path

from mappymatch import package_root
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.readers.osm_readers import read_osm_nxmap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.matchers.line_snap import LineSnapMatcher
from mappymatch.utils.geo import geofence_from_trace


PLOT = True

if PLOT:
    import webbrowser

    from mappymatch.utils.plot import plot_matches

trace = Trace.from_csv(package_root() / "resources/traces/sample_trace_3.csv")

# generate a geofence polygon that surrounds the trace; units are in meters;
# this is used to query OSM for a small map that we can match to
geofence = Geofence.from_trace(trace, padding=1e3)

# uses osmnx to pull a networkx map from the OSM database
nx_map = NxMap.from_osm_network(geofence)

lcss_matcher = LCSSMatcher(nx_map)
snap_matcher = LineSnapMatcher(nx_map)

lcss_matches = lcss_matcher.match_trace(trace)
snap_matches = snap_matcher.match_trace(trace)

if PLOT:
    lcss_file = Path("lcss_matches.html")
    lmap = plot_matches(lcss_matches, road_map=nx_map)
    lmap.save(str(lcss_file))
    webbrowser.open(lcss_file.absolute().as_uri())

    smap_file = Path("snap_matches.html")
    smap = plot_matches(snap_matches, road_map=nx_map)
    smap.save(str(smap_file))
    webbrowser.open(smap_file.absolute().as_uri())
