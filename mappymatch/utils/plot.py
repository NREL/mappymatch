from typing import List
import folium

import geopandas as gpd
import pandas as pd

from shapely.geometry import Point
from mappymatch.constructs.match import Match
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from mappymatch.constructs.trace import Trace
from mappymatch.utils.geo import geofence_from_trace
from mappymatch.maps.nx.readers.osm_readers import read_osm_nxmap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch import root

import matplotlib.pyplot as plt

def plot_geofence(geofence, m=None):
    """
    Plot geofence.

    TODO: E: Determine if this is a good use of a single letter variable name

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


def plot_trace(trace, m=None, point_color="yellow", line_color="green"):
    """
    Plot a trace.

    Args:
        trace: The trace.
        m: the folium map to plot on
        point_color: The color the points will be plotted in.
        line_color: The color for lines.

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
            location=(c.y, c.x), radius=5, color=point_color, tooltip=i
        ).add_to(m)

    folium.PolyLine(
        [(p.y, p.x) for p in trace.coords], color=line_color
    ).add_to(m)

    return m


def plot_matches(matches: List[Match], road_map: NxMap):
    """
    Plots a trace and the relevant matches on a folium map.

    Args:
    matches: The matches.
    road_map: The road map.

    Returns:
        A folium map with trace and matches plotted.
    """

    def _match_to_road(m):
        """Private function."""
        d = {"road_id": m.road.road_id}

        edge_data = road_map.g.get_edge_data(
            m.road.origin_junction_id, m.road.dest_junction_id
        )

        road_key = list(edge_data.keys())[0]

        # TODO: this should be generic over all road maps
        geom_key = road_map._geom_key  # type: ignore

        road_geom = edge_data[road_key][geom_key]

        d["geom"] = road_geom

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
    road_gdf = gpd.GeoDataFrame(
        road_df, geometry=road_df.geom, crs=XY_CRS
    ).drop(columns=["geom"])
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    coord_df = pd.DataFrame([_match_to_coord(m) for m in matches if m.road])

    coord_gdf = gpd.GeoDataFrame(
        coord_df, geometry=coord_df.geom, crs=XY_CRS
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

    # The road_df and coord_df variables for our plot_match_distances function later on are available here for plotting.
    # calling the plotting function with coordinate data frames already loaded in memory.
    plot_match_distances(coord_df)

    return fmap


def plot_map(tmap: NxMap, m=None):
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
            [(lat, lon) for lon, lat in t.geometry.coords], color="red"
        ).add_to(m)

    return m


def plot_match_distances(matches):
    """
        Summary: Plot the points deviance from known roads with matplotlib.

        Issues:
            we have two different dataframes one labeled with gdf and the other with df. --> to resolve this, the gdf labeled data frames have been changed to df labels.

        Args:
            coord_df (pandas dataframe): coords of guessed points in the area.
    """

    y = [m.distance for m in matches]
    x = [x for x in range(0, len(y))]  # this line create placeholder values for x axis

    plt.figure(figsize=(15, 7))
    plt.autoscale(
        enable=True
    )
    plt.scatter(
        x, y
    )
    plt.title("Distance To Nearest Road")
    plt.ylabel("Meters")
    plt.xlabel(
        "Point Along The Path"
    )
    plt.show()


def plot_prep(file_path):  #
    """
    Summary:
       provided a file path, the plot_prep function creates a trace, geofence, road_map, and matcher using LCSSMatcher and then passes the matches object to the plot_matches function. This function generates a fmap, but it also runs the plot_match_distances function before it finishes executing. With some tweaking this can be customized to the users preferences.

    Args:
        file_path (str, optional): _description_. Defaults to 'resources/traces/sample_trace_1.csv'.
    """
    try:
        trace = Trace.from_csv(root() / f"{file_path}")
    except Exception:
        trace = Trace.from_csv(
            f"{file_path}"
        )  # catches any file entry errors.
    geofence = geofence_from_trace(trace, padding=1e3)
    road_map = read_osm_nxmap(geofence)
    matcher = LCSSMatcher(road_map)
    matches = matcher.match_trace(trace)
    fmap_result = plot_matches(
        matches, road_map
    )  # call the plot_matches function which will plot the matches with matplotlib
    return fmap_result

file_path = "resources/traces/sample_trace_3.csv"

fmap_result = plot_prep(file_path)
