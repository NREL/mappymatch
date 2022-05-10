from typing import List, Optional #TODO - Optional is not used.
import folium
import geopandas as gpd #TODO - we removed geopandas I believe.
import pandas as pd
import numpy as np
from shapely.geometry import Point
from mappymatch.constructs.match import Match
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from mappymatch.constructs.trace import Trace
from mappymatch.utils.geo import geofence_from_trace
from mappymatch.maps.nx.readers.osm_readers import read_osm_nxmap
from mappymatch.maps.map_interface import MapInterface #TODO - MapInterface is not used.
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch import root

# plotting imports from mappymatch utils as well as matplotlib
#todo - all of the imports from mappymatch.utils.plot are not being used in this file.
from mappymatch.utils.plot import (
    plot_geofence,
    plot_trace,
    plot_matches,
    plot_map,
)
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

#ADD - functions from the visualization file
def match_to_road(m):
    d = {"road_id": m.road.road_id}

    metadata = m.road.metadata
    u = metadata["u"]
    v = metadata["v"]

    edge_data = road_map.g.get_edge_data(u, v)

    road_key = list(edge_data.keys())[0]

    # TODO: this should be generic over all road maps
    geom_key = road_map._geom_key # todo: needs someone familiar with the code to fix this. road_map is not defined.

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


def plot_match_distances(matches: MatchResult): # TODO: -- MatchResult is not a defined Element.
    # build and display plots here.
    """
    Summary:

        matches gets passed to plot_match_distances after it is calculated as follows.

        trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")
        geofence = geofence_from_trace(
            trace, padding=1e3
        )
        road_map = read_osm_nxmap(geofence)
        matcher = LCSSMatcher(road_map)
        matches = matcher.match_trace(trace)

    Args:
        matches (MatchResult): _description_
    """

    #! Road Data Frame Section
    # define a pandas data frame containing the list of matches (each represented by m) where m.road = True
    road_df = pd.DataFrame([match_to_road(m) for m in matches if m.road])
    road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]

    # TODO: -- the data frame below still utilizes geopandas. Is this what you want to use or is there something else that should be implemented here?
    road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
        columns=["geom"]
    ) # drop the geom column from the road_gdf data frame.
    road_gdf = road_gdf.to_crs(LATLON_CRS)

    #! Coordinate Data Frame Section
    coord_df = pd.DataFrame([match_to_coord(m) for m in matches if m.road])
    # TODO: -- the data frame below still utilizes geopandas.
    coord_gdf = gpd.GeoDataFrame(
        coord_df, geometry=coord_df.geom, crs=XY_CRS
    ).drop(columns=["geom"]) # drop the geom column from the coord_df data frame.
    coord_gdf = coord_gdf.to_crs(
        LATLON_CRS
    )  # convert coordinates to latlon_crs format.

    mid_i = int(len(coord_gdf) / 2) # find the middle index of the coord_gdf data frame.
    mid_coord = coord_gdf.iloc[mid_i].geometry # answer the question: what is the middle coordinate?

    y = coord_df.distance  # the distances from the expected line. Deviance.
    x = [x for x in range(0, len(y))]  # create blanks for x axis

    for coord in coord_gdf.itertuples(): # for every coordinate tuple within coord_gdf ...
        x_coord = coord.geometry.x # identify the x coordinate geometry.
        y_coord = coord.geometry.y # identify the y coordinate geometry.

    for road in road_gdf.itertuples(): # for every road in the road_gdf data frame...
        full_line = [(lat, lon) for lon, lat in road.geometry.coords] # identify the full line of that road in lat,long tuples.

    #! Plotting Section
    plt.figure(figsize=(15, 7)) # create a figure sized 15 x 7
    plt.autoscale(enable=True) # autoscale the figure's contents to the data once it is plotted.
    #todo ---- what was the purpose of plt.stem? -->  plt.stem(x, y)
    plt.scatter(x, y) # create a scatter plot of our x (blanks), and our y (deviance from expected line) values.
    plt.title("Distance To Nearest Road") # create a title for our plot.
    plt.ylabel("Meters") # establish the y axis label "Meters"
    plt.xlabel("Point Along The Path") # label the x axis label "Point Along The Path"
    plt.show() # print the plot.

def plot_prep(file_path='resources/traces/sample_trace_1.csv'): #
    """
    Summary:
       provided a file path, the plot_prep function creates a trace, geofence, road_map, and matcher using LCSSMatcher and then passes the matches object to the plot_match_distances function.

    Args:
        file_path (str, optional): _description_. Defaults to 'resources/traces/sample_trace_1.csv'.
    """
    trace = Trace.from_csv(root() / f"{file_path}")
    geofence = geofence_from_trace(
        trace, padding=1e3
    )
    road_map = read_osm_nxmap(geofence)
    matcher = LCSSMatcher(road_map)
    matches = matcher.match_trace(trace)

    plot_match_distances(matches) # call plot match distances with the matches to generate insight plots.

plot_prep()