from typing import List, Optional, Union

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from pyproj import CRS
from shapely.geometry import Point

from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.matcher_interface import MatchResult
from mappymatch.utils.crs import LATLON_CRS, XY_CRS


def plot_geofence(geofence: Geofence, m: Optional[folium.Map] = None):
    """
    Plot geofence.

    Args:
        geofence: The geofence to plot
        m: the folium map to plot on

    Returns:
        The updated folium map with the geofence.
    """
    if not geofence.crs == LATLON_CRS:
        raise NotImplementedError(
            "can currently only plot a geofence with lat lon crs"
        )

    if not m:
        c = geofence.geometry.centroid.coords[0]
        m = folium.Map(location=[c[1], c[0]], zoom_start=11)

    folium.GeoJson(geofence.geometry).add_to(m)

    return m


def plot_trace(
    trace: Trace,
    m: Optional[folium.Map] = None,
    point_color: str = "black",
    line_color: Optional[str] = "green",
):
    """
    Plot a trace.

    Args:
        trace: The trace.
        m: the folium map to plot on
        point_color: The color the points will be plotted in.
        line_color: The color for lines. If None, no lines will be plotted.

    Returns:
        An updated folium map with a plot of trace.
    """

    if not trace.crs == LATLON_CRS:
        trace = trace.to_crs(LATLON_CRS)

    if not m:
        mid_coord = trace.coords[int(len(trace) / 2)]
        m = folium.Map(location=[mid_coord.y, mid_coord.x], zoom_start=11)

    for i, c in enumerate(trace.coords):
        folium.Circle(
            location=(c.y, c.x),
            radius=5,
            color=point_color,
            tooltip=i,
            fill=True,
            fill_opacity=0.8,
            fill_color=point_color,
        ).add_to(m)

    if line_color is not None:
        folium.PolyLine(
            [(p.y, p.x) for p in trace.coords], color=line_color
        ).add_to(m)

    return m


def plot_matches(matches: Union[MatchResult, List[Match]], crs=XY_CRS):
    """
    Plots a trace and the relevant matches on a folium map.

    Args:
    matches: A list of matches or a MatchResult.
    crs: what crs to plot in. Defaults to XY_CRS.

    Returns:
        A folium map with trace and matches plotted.
    """
    if isinstance(matches, MatchResult):
        matches = matches.matches

    def _match_to_road(m):
        """Private function."""
        d = {"road_id": m.road.road_id, "geom": m.road.geom}
        return d

    def _match_to_coord(m):
        """Private function."""
        d = {
            "road_id": m.road.road_id,
            "geom": Point(m.coordinate.x, m.coordinate.y),
            "distance": m.distance,
        }

        return d

    road_df = pd.DataFrame([_match_to_road(m) for m in matches if m.road])
    road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=crs).drop(
        columns=["geom"]
    )
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    coord_df = pd.DataFrame([_match_to_coord(m) for m in matches if m.road])

    coord_gdf = gpd.GeoDataFrame(
        coord_df, geometry=coord_df.geom, crs=crs
    ).drop(columns=["geom"])
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


def plot_map(tmap: NxMap, m: Optional[folium.Map] = None):
    """
    Plot the roads on an NxMap.

    Args:
        tmap: The Nxmap to plot.
        m: the folium map to add to

    Returns:
        The folium map with the roads plotted.
    """

    # TODO make this generic to all map types, not just NxMap
    roads = list(tmap.g.edges(data=True))
    road_df = pd.DataFrame([r[2] for r in roads])
    gdf = gpd.GeoDataFrame(
        road_df, geometry=road_df[tmap._geom_key], crs=tmap.crs
    )
    if gdf.crs != LATLON_CRS:
        gdf = gdf.to_crs(LATLON_CRS)

    if not m:
        c = gdf.iloc[int(len(gdf) / 2)].geometry.centroid.coords[0]
        m = folium.Map(location=[c[1], c[0]], zoom_start=11)

    for t in gdf.itertuples():
        folium.PolyLine(
            [(lat, lon) for lon, lat in t.geometry.coords],
            color="red",
        ).add_to(m)

    return m


def plot_match_distances(matches: MatchResult):
    """
    Plot the points deviance from known roads with matplotlib.

    Args:
        matches (MatchResult): The coordinates of guessed points in the area in the form of a MatchResult object.
    """

    y = [
        m.distance for m in matches.matches
    ]  # y contains distances to the expected line for all of the matches which will be plotted on the y-axis.
    x = [
        i for i in range(0, len(y))
    ]  # x contains placeholder values for every y value (distance measurement) along the x-axis.

    plt.figure(figsize=(15, 7))
    plt.autoscale(enable=True)
    plt.scatter(x, y)
    plt.title("Distance To Nearest Road")
    plt.ylabel("Meters")
    plt.xlabel("Point Along The Path")
    plt.show()


def plot_path(
    path: List[Road],
    crs: CRS,
    m: Optional[folium.Map] = None,
    line_color="red",
    line_weight=10,
    line_opacity=0.8,
):
    """
    Plot a list of roads.

    Args:
        path: The path to plot.
        crs: The crs of the path.
        m: The folium map to add to.
        line_color: The color of the line.
        line_weight: The weight of the line.
        line_opacity: The opacity of the line.
    """
    road_df = pd.DataFrame([{"geom": r.geom} for r in path])
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=crs)
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    if m is None:
        mid_i = int(len(road_gdf) / 2)
        mid_coord = road_gdf.iloc[mid_i].geometry.coords[0]

        m = folium.Map(location=[mid_coord[1], mid_coord[0]], zoom_start=11)

    for i, road in enumerate(road_gdf.itertuples()):
        folium.PolyLine(
            [(lat, lon) for lon, lat in road.geometry.coords],
            color=line_color,
            tooltip=i,
            weight=line_weight,
            opacity=line_opacity,
        ).add_to(m)

    return m
