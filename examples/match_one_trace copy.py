from pathlib import Path
from yamm.constructs.trace import Trace
from yamm.utils.geo import geofence_from_trace
from yamm.maps.nx.readers.osm_readers import read_osm_nxmap
from yamm.matchers.lcss.lcss import LCSSMatcher
from yamm import root

PLOT = True

if PLOT:
    from yamm.utils.plot import plot_geofence, plot_trace, plot_matches
    import webbrowser

trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")

# generate a geofence polygon that surrounds the trace; units are in meters;
# this is used to query OSM for a small map that we can match to
geofence = geofence_from_trace(trace, padding=1e3)

# uses osmnx to pull a networkx map from the OSM database
nx_map = read_osm_nxmap(geofence)

matcher = LCSSMatcher(nx_map)

matches = matcher.match_trace(trace)

if PLOT:
    tmap_file = Path("trace_map.html")
    tmap = plot_trace(trace, plot_geofence(geofence))
    tmap.save(str(tmap_file))
    webbrowser.open(tmap_file.absolute().as_uri())

    mmap_file = Path("matches_map.html")
    mmap = plot_matches(matches, road_map=nx_map)
    mmap.save(str(mmap_file))
    webbrowser.open(mmap_file.absolute().as_uri())
