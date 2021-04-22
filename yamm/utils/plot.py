from typing import List

import folium

import pandas as pd
import geopandas as gpd

from pyproj import Transformer

from yamm.constructs.match import Match
from yamm.constructs.trace import Trace
from yamm.maps.map_interface import MapInterface
from yamm.utils.crs import XY_CRS, LATLON_CRS


def plot_matches(trace: Trace, matches: List[Match], road_map: MapInterface):
    """
    plots a trace and the relevant matches on a folium map

    :param trace: the trace
    :param matches: the matches
    :param road_map: the road map

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

    df = pd.DataFrame([match_to_road(m) for m in matches])
    df = df.loc[df.road_id.shift() != df.road_id]
    gdf = gpd.GeoDataFrame(df, geometry=df.geom, crs=XY_CRS).drop(columns=["geom"])
    gdf = gdf.to_crs(LATLON_CRS)

    mid_i = int(len(trace.coords) / 2)
    mid_coord = trace.coords[mid_i].to_crs(LATLON_CRS)

    fmap = folium.Map(location=[mid_coord.x, mid_coord.y], zoom_start=11)

    xs = [c.x for c in trace.downsample(1000).coords]
    ys = [c.y for c in trace.downsample(1000).coords]
    transformer = Transformer.from_crs(XY_CRS, LATLON_CRS)
    lats, lons = transformer.transform(xs, ys)

    for lat, lon in zip(lats, lons):
        folium.Circle(location=(lat, lon), radius=5).add_to(fmap)

    for road in gdf.itertuples():
        folium.PolyLine([(lat, lon) for lon, lat in road.geometry.coords], color="red").add_to(fmap)

    return fmap