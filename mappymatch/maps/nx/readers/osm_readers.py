from __future__ import annotations

import logging as log
from enum import Enum

import networkx as nx
from shapely.geometry import LineString

from mappymatch.constructs.geofence import Geofence
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from mappymatch.utils.exceptions import MapException

log.basicConfig(level=log.INFO)


METERS_TO_KM = 1 / 1000
DEFAULT_MPH = 30


class NetworkType(Enum):
    """
    Enumerator for Network Types supported by osmnx.
    """

    ALL_PRIVATE = "all_private"
    ALL = "all"
    BIKE = "bike"
    DRIVE = "drive"
    DRIVE_SERVICE = "drive_service"
    WALK = "walk"


def nx_graph_from_osmnx(
    geofence: Geofence, network_type: NetworkType, xy: bool = True
) -> nx.MultiDiGraph:
    """
    Build a networkx graph from OSM data

    Args:
        geofence: the geofence to clip the graph to
        network_type: the network type to use for the graph
        xy: whether to use xy coordinates or lat/lon

    Returns:
        a networkx graph of the OSM network
    """
    try:
        import osmnx as ox
    except ImportError:
        raise MapException(
            "osmnx is not installed but is required for this map type"
        )
    ox.settings.log_console = False

    raw_graph = ox.graph_from_polygon(
        geofence.geometry, network_type=network_type.value
    )
    return parse_osmnx_graph(raw_graph, network_type)


def parse_osmnx_graph(
    graph: nx.MultiDiGraph,
    network_type: NetworkType,
    xy: bool = True,
) -> nx.MultiDiGraph:
    """
    Parse the raw osmnx graph into a graph that we can use with our NxMap

    Args:
        geofence: the geofence to clip the graph to
        xy: whether to use xy coordinates or lat/lon
        network_type: the network type to use for the graph

    Returns:
        a cleaned networkx graph of the OSM network
    """
    try:
        import osmnx as ox
    except ImportError:
        raise MapException(
            "osmnx is not installed but is required for this map type"
        )
    ox.settings.log_console = False
    g = graph

    if xy:
        g = ox.project_graph(g, XY_CRS)
        crs = XY_CRS
    else:
        crs = LATLON_CRS

    g = ox.add_edge_speeds(g)
    g = ox.add_edge_travel_times(g)

    length_meters = nx.get_edge_attributes(g, "length")
    kilometers = {k: v * METERS_TO_KM for k, v in length_meters.items()}
    nx.set_edge_attributes(g, kilometers, "kilometers")

    # this makes sure there are no graph 'dead-ends'
    sg_components = nx.strongly_connected_components(g)

    if not sg_components:
        raise MapException(
            "road network has no strongly connected components and is not routable; "
            "check polygon boundaries."
        )

    g = nx.MultiDiGraph(g.subgraph(max(sg_components, key=len)))

    no_geom = 0
    for u, v, d in g.edges(data=True):
        if "geometry" not in d:
            # we'll build a pseudo-geometry using the x, y data from the nodes
            unode = g.nodes[u]
            vnode = g.nodes[v]
            line = LineString(
                [(unode["x"], unode["y"]), (vnode["x"], vnode["y"])]
            )
            d["geometry"] = line
            no_geom += 1
    if no_geom:
        print(
            f"Warning: found {no_geom} links with no geometry; creating geometries from the node lat/lon"
        )

    g = compress(g)

    g.graph["crs"] = crs

    # TODO: these should all be sourced from the same location
    g.graph["distance_weight"] = "kilometers"
    g.graph["time_weight"] = "travel_time"
    g.graph["geometry_key"] = "geometry"
    g.graph["network_type"] = network_type.value

    return g


def compress(g) -> nx.MultiDiGraph:
    """
    a hacky way to delete unnecessary data on the networkx graph

    Args:
        g: the networkx graph to compress

    Returns:
        the compressed networkx graph
    """
    keys_to_delete = [
        "oneway",
        "ref",
        "access",
        "lanes",
        "name",
        "maxspeed",
        "highway",
        "length",
        "speed_kph",
        "osmid",
        "street_count",
        "junction",
        "bridge",
        "tunnel",
        "y",
        "x",
    ]

    for _, _, d in g.edges(data=True):
        for k in keys_to_delete:
            try:
                del d[k]
            except KeyError:
                continue

    for _, d in g.nodes(data=True):
        for k in keys_to_delete:
            try:
                del d[k]
            except KeyError:
                continue

    return g
