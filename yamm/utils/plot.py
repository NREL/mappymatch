from typing import List, Optional

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


def plot_trace(trace, m=None, point_color="yellow", line_color="green"):
    if not trace.crs == LATLON_CRS:
        trace = trace.to_crs(LATLON_CRS)

    if not m:
        mid_coord = trace.coords[int(len(trace) / 2)]
        m = folium.Map(location=[mid_coord.y, mid_coord.x], zoom_start=11)

    for i, c in enumerate(trace.coords):
        folium.Circle(
            location=(c.y, c.x), radius=5, color=point_color, tooltip=i
        ).add_to(m)

    folium.PolyLine([(p.y, p.x) for p in trace.coords], color=line_color).add_to(m)

    return m


def plot_matches(matches: List[Match], road_map: MapInterface):
    """
    plots a trace and the relevant matches on a folium map

    :param matches: the matches
    :param road_map: the road map

    :return: the folium map
    """

    def match_to_road(m):
        d = {"road_id": m.road.road_id}

        metadata = m.road.metadata
        u = metadata["u"]
        v = metadata["v"]

        edge_data = road_map.g.get_edge_data(u, v)
        road_geom = edge_data[m.road.road_id]["geom"]

        d["geom"] = road_geom

        return d

    def match_to_coord(m):
        d = {
            "road_id": m.road.road_id,
            "geom": Point(m.coordinate.x, m.coordinate.y),
            "distance": m.distance,
        }

        return d

    road_df = pd.DataFrame([match_to_road(m) for m in matches if m.road])
    road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
        columns=["geom"]
    )
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    coord_df = pd.DataFrame([match_to_coord(m) for m in matches if m.road])

    coord_gdf = gpd.GeoDataFrame(coord_df, geometry=coord_df.geom, crs=XY_CRS).drop(
        columns=["geom"]
    )
    coord_gdf = coord_gdf.to_crs(LATLON_CRS)

    mid_i = int(len(coord_gdf) / 2)
    mid_coord = coord_gdf.iloc[mid_i].geometry

    fmap = folium.Map(location=[mid_coord.y, mid_coord.x], zoom_start=11)

    for coord in coord_gdf.itertuples():
        folium.Circle(
            location=(coord.geometry.y, coord.geometry.x),
            radius=5,
            tooltip=f"road_id: {coord.road_id}\ndistance: {coord.distance}",
        ).add_to(fmap)

    for road in road_gdf.itertuples():
        folium.PolyLine(
            [(lat, lon) for lon, lat in road.geometry.coords],
            color="red",
            tooltip=road.road_id,
        ).add_to(fmap)

    return fmap


def plot_map(tmap: MapInterface, m=None):
    roads = list(tmap.g.edges(data=True))
    road_df = pd.DataFrame([r[2] for r in roads])
    gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
        columns=["geom"]
    )
    gdf = gdf.to_crs(LATLON_CRS)

    if not m:
        c = gdf.iloc[int(len(gdf) / 2)].geometry.centroid.coords[0]
        m = folium.Map(location=[c[1], c[0]], zoom_start=11)

    for t in gdf.itertuples():
        folium.PolyLine(
            [(lat, lon) for lon, lat in t.geometry.coords], color="red"
        ).add_to(m)

    return m
