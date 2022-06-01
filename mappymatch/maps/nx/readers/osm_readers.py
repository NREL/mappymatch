import logging as log
from enum import Enum

import networkx as nx
import osmnx as ox
from shapely.geometry import LineString

from mappymatch.constructs.geofence import Geofence
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from mappymatch.utils.exceptions import MapException

ox.config(log_console=False)
log.basicConfig(level=log.INFO)

DEFAULT_MPH = 30
_unit_conversion = {
    "mph": 1,
    "kmph": 0.621371,
}
METERS_TO_KM = 1 / 1000


class NetworkType(Enum):
    """
    Network Types suuported by osmnx
    """

    all_private = "all_private"
    all = "all"
    bike = "bike"
    drive = "drive"
    drive_service = "drive_service"
    walk = "walk"


def read_osm_nxmap(
    geofence: Geofence,
    xy: bool = True,
    network_type: NetworkType = NetworkType.drive,
) -> NxMap:
    """
    Read an OSM network graph into a NxMap

    Args:
        geofence: the geofence to clip the graph to
        xy: whether to use xy coordinates or lat/lon
        network_type: the network type to use for the graph

    Returns:
        a NxMap
    """
    if geofence.crs != LATLON_CRS:
        raise TypeError(
            f"the geofence must in the epsg:4326 crs but got {geofence.crs.to_authority()}"
        )

    g = get_osm_networkx_graph(geofence, xy, network_type)

    return NxMap(g)


def parse_road_network_graph(g) -> nx.MultiDiGraph:
    """
    Parse the road network graph to add additional attributes

    Args:
        g: the road network graph

    Returns:
        the parsed road network graph
    """
    length_meters: dict
    length_meters = nx.get_edge_attributes(g, "length")
    kilometers = {k: v * METERS_TO_KM for k, v in length_meters.items()}
    nx.set_edge_attributes(g, kilometers, "kilometers")

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


def get_osm_networkx_graph(
    geofence: Geofence,
    xy: bool = True,
    network_type: NetworkType = NetworkType.drive,
) -> nx.MultiDiGraph:
    """
    Get an OSM network graph

    Args:
        geofence: the geofence to clip the graph to
        xy: whether to use xy coordinates or lat/lon
        network_type: the network type to use for the graph

    Returns:
        a networkx graph of the OSM network
    """
    g = ox.graph_from_polygon(
        geofence.geometry, network_type=network_type.value
    )

    if xy:
        g = ox.project_graph(g, XY_CRS)
        crs = XY_CRS
    else:
        crs = LATLON_CRS

    g = ox.add_edge_speeds(g)
    g = ox.add_edge_travel_times(g)
    g = parse_road_network_graph(g)

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
        d["road_id"] = f"{u}-{v}"
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
    g.graph["road_id_key"] = "road_id"
    g.graph["network_type"] = network_type.value

    return g
