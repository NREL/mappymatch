from typing import List

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from yamm.constructs.match import Match
from yamm.constructs.trace import Trace
from yamm.maps.map_interface import MapInterface
from yamm.utils.crs import XY_CRS, LATLON_CRS


def plot_geofence(geofence, m=None):
    if not geofence.crs == LATLON_CRS:
        raise NotImplementedError("can currently only plot a geofence with lat lon crs")

    if not m:
        c = geofence.geometry.centroid.coords[0]
        m = folium.Map(location=[c[1], c[0]], zoom_start=11)

    folium.GeoJson(geofence.geometry).add_to(m)

    return m


def plot_trace(trace, m=None, color='red'):
    if not trace.crs == LATLON_CRS:
        trace = trace.to_crs(LATLON_CRS)

    if not m:
        mid_coord = trace.coords[int(len(trace) / 2)]
        m = folium.Map(location=[mid_coord.y, mid_coord.x], zoom_start=11)

    for c in trace.coords:
        folium.Circle(location=(c.y, c.x), radius=5, color=color).add_to(m)

    return m


def plot_matches(trace: Trace, matches: List[Match], road_map: MapInterface, npoints: int):
    """
    plots a trace and the relevant matches on a folium map

    :param trace: the trace
    :param matches: the matches
    :param road_map: the road map
    :param npoints: how many trace points to plot? useful in you have a large trace

    :return: the folium map
    """

    def match_to_road(m):
        d = {}

        d['road_id'] = m.road.road_id
        metadata = m.road.metadata
        u = metadata['u']
        v = metadata['v']

        edge_data = road_map.g.get_edge_data(u, v)
        road_geom = edge_data[m.road.road_id]['geom']

        d['geom'] = road_geom

        return d

    def match_to_coord(m):
        d = {}

        d['road_id'] = m.road.road_id
        d['geom'] = Point(m.coordinate.x, m.coordinate.y)
        d['distance'] = m.distance
        return d

    road_df = pd.DataFrame([match_to_road(m) for m in matches if m.road])
    road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(columns=["geom"])
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    coord_df = pd.DataFrame([match_to_coord(m) for m in matches if m.road])
    index = [i for i in np.linspace(1, len(coord_df.index) - 1, npoints - 2).astype(int)]
    coord_df = coord_df.loc[index]

    coord_gdf = gpd.GeoDataFrame(coord_df, geometry=coord_df.geom, crs=XY_CRS).drop(columns=["geom"])
    coord_gdf = coord_gdf.to_crs(LATLON_CRS)

    mid_i = int(len(trace) / 2)
    mid_coord = trace.coords[mid_i].to_crs(LATLON_CRS)

    fmap = folium.Map(location=[mid_coord.x, mid_coord.y], zoom_start=11)

    for coord in coord_gdf.itertuples():
        folium.Circle(location=(coord.geometry.y, coord.geometry.x), radius=5,
                      tooltip=f"road_id: {coord.road_id}\ndistance: {coord.distance}").add_to(fmap)

    for road in road_gdf.itertuples():
        folium.PolyLine([(lat, lon) for lon, lat in road.geometry.coords], color="red", tooltip=road.road_id).add_to(
            fmap)

    return fmap
