import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from mappymatch.constructs.trace import Trace
from mappymatch.utils.geo import geofence_from_trace
from mappymatch.maps.nx.readers.osm_readers import read_osm_nxmap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.plot import (
    plot_geofence,
    plot_trace,
    plot_matches,
    plot_map,
)
from mappymatch import root
from mappymatch.utils.crs import XY_CRS, LATLON_CRS
from typing import List, Optional

import folium
from shapely.geometry import Point

from mappymatch.constructs.match import Match
from mappymatch.maps.map_interface import MapInterface

# functions
def match_to_road(m):
    d = {"road_id": m.road.road_id}

    metadata = m.road.metadata
    u = metadata["u"]
    v = metadata["v"]

    edge_data = road_map.g.get_edge_data(u, v)

    road_key = list(edge_data.keys())[0]

    # TODO: this should be generic over all road maps
    geom_key = road_map._geom_key

    road_geom = edge_data[road_key][geom_key]

    d["geom"] = road_geom

    return d


def match_to_coord(m):
    d = {
        "road_id": m.road.road_id,
        "geom": Point(m.coordinate.x, m.coordinate.y),
        "distance": m.distance,
    }

    return d


# from mappymatch import match_to_road

#%debug
from mappymatch.constructs.match import Match

# trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")

trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")
geofence = geofence_from_trace(
    trace, padding=1e3
)  # TODO --> the fence could be insufficiently bounding points that are still being used in the dataframes.
road_map = read_osm_nxmap(geofence)
matcher = LCSSMatcher(road_map)
matches = matcher.match_trace(trace)

# TODO - remove these and make them imports
road_df = pd.DataFrame([match_to_road(m) for m in matches if m.road])
road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
    columns=["geom"]
)
road_gdf = road_gdf.to_crs(LATLON_CRS)

coord_df = pd.DataFrame([match_to_coord(m) for m in matches if m.road])

coord_gdf = gpd.GeoDataFrame(
    coord_df, geometry=coord_df.geom, crs=XY_CRS
).drop(columns=["geom"])

coord_gdf = coord_gdf.to_crs(
    LATLON_CRS
)  # convert coordinates to latlon_crs format.

mid_i = int(len(coord_gdf) / 2)
mid_coord = coord_gdf.iloc[mid_i].geometry

y = coord_df.distance  # the distances from the expected line. Deviance.
x = [x for x in range(0, len(y))]  # create blanks for x axis
# y = np.exp(np.sin(x))

for coord in coord_gdf.itertuples():
    x_coord = coord.geometry.x
    y_coord = coord.geometry.y

for road in road_gdf.itertuples():
    full_line = [(lat, lon) for lon, lat in road.geometry.coords]


plt.figure(figsize=(15, 7))
plt.autoscale(enable=True)
# plt.stem(x, y)
plt.scatter(x, y)
plt.title("Distance To Nearest Road")
plt.ylabel("Meters")
plt.xlabel("Point Along The Path")
plt.show()
