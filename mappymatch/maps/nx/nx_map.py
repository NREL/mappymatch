from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List, Union

import networkx as nx
import numpy as np
import osmnx as ox
import rtree as rt
from shapely.geometry import LineString, Point

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.road import Road
from mappymatch.maps.map_interface import MapInterface, PathWeight
from mappymatch.utils.crs import CRS, LATLON_CRS, XY_CRS
from mappymatch.utils.exceptions import MapException

DEFAULT_DISTANCE_WEIGHT = "kilometers"
DEFAULT_TIME_WEIGHT = "minutes"
DEFAULT_GEOMETRY_KEY = "geometry"
DEFAULT_ROAD_ID_KEY = "road_id"

METERS_TO_KM = 1 / 1000
DEFAULT_MPH = 30

_unit_conversion = {
    "mph": 1,
    "kmph": 0.621371,
}


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


DEFAULT_METADATA_KEY = "metadata"


class NxMap(MapInterface):
    """
    A road map that uses a networkx graph to represent its roads.

    Attributes:
        g: The networkx graph that represents the road map
        crs: The coordinate reference system of the map
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.g = graph

        if "crs" not in graph.graph:
            raise ValueError(
                "Input graph must have pyproj crs;"
                "You can set it like: `graph.graph['crs'] = pyproj.CRS('EPSG:4326')`"
            )

        crs = graph.graph["crs"]

        if not isinstance(crs, CRS):
            raise TypeError(
                "Input graph must have pyproj crs;"
                "You can set it like: `graph.graph['crs'] = pyproj.CRS('EPSG:4326')`"
            )

        self.crs = crs

        dist_weight = graph.graph.get(
            "distance_weight", DEFAULT_DISTANCE_WEIGHT
        )
        time_weight = graph.graph.get("time_weight", DEFAULT_TIME_WEIGHT)
        geom_key = graph.graph.get("geometry_key", DEFAULT_GEOMETRY_KEY)
        road_id_key = graph.graph.get("road_id", DEFAULT_ROAD_ID_KEY)
        metadata_key = graph.graph.get("metadata", DEFAULT_METADATA_KEY)

        self._dist_weight = dist_weight
        self._time_weight = time_weight
        self._geom_key = geom_key
        self._road_id_key = road_id_key
        self._metadata_key = metadata_key

        self._nodes = [nid for nid in self.g.nodes()]
        self._roads = self._build_rtree()

    def _build_rtree(self) -> List[Road]:
        road_lookup = []

        idx = rt.index.Index()
        for i, gtuple in enumerate(self.g.edges(data=True, keys=True)):
            u, v, k, d = gtuple
            # rid = (u, v, k)
            geom = d[self._geom_key]
            # segment = list(geom.coords)
            box = geom.bounds
            idx.insert(i, box)

            metadata = d.get(self._metadata_key)

            metadata[self._dist_weight] = d.get(self._dist_weight)
            metadata[self._time_weight] = d.get(self._time_weight)

            road = Road(
                d[self._road_id_key],
                d[self._geom_key],
                origin_junction_id=u,
                dest_junction_id=v,
                metadata=metadata,
            )
            road_lookup.append(road)

        self.rtree = idx
        return road_lookup

    def __str__(self):
        output_lines = [
            "Mappymatch NxMap object",
            f"roads: {len(self._roads)} Road objects",
            f"graph: {self.g}",
        ]
        return "\n".join(output_lines)

    def __repr__(self):
        return self.__str__()

    @property
    def roads(self) -> List[Road]:
        return self._roads

    @classmethod
    def from_file(cls, file: Union[str, Path]) -> NxMap:
        """
        Build a NxMap instance from a file

        Args:
            file: The graph pickle file to load the graph from

        Returns:
            A NxMap instance
        """
        p = Path(file)
        if not p.suffix == ".pickle":
            raise TypeError("NxMap only supports pickle files")

        g = nx.readwrite.read_gpickle(file)

        return NxMap(g)

    @classmethod
    def from_geofence(
        cls,
        geofence: Geofence,
        xy: bool = True,
        network_type: NetworkType = NetworkType.DRIVE,
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

        raw_graph = ox.graph_from_polygon(
            geofence.geometry, network_type=network_type.value
        )
        cleaned_graph = parse_osmnx_graph(raw_graph, network_type, xy)

        return NxMap(cleaned_graph)

    def to_file(self, outfile: Union[str, Path]):
        """
        Save the graph to a pickle file

        Args:
            outfile: The file to save the graph to
        """
        nx.write_gpickle(self.g, str(outfile))

    def nearest_road(self, coord: Coordinate, buffer: float = 10.0) -> Road:
        """
        A helper function to get the nearest road.

        Args:
            coord: The coordinate to find the nearest road to
            buffer: The buffer to search around the coordinate

        Returns:
            The nearest road to the coordinate
        """
        if coord.crs != self.crs:
            raise ValueError(
                f"crs of origin {coord.crs} must match crs of map {self.crs}"
            )
        nearest_candidates = list(
            self.rtree.nearest(coord.geom.buffer(buffer).bounds, 1)
        )

        if len(nearest_candidates) == 0:
            raise ValueError(f"No roads found for {coord}")
        elif len(nearest_candidates) == 1:
            nearest_index = nearest_candidates[0]
        else:
            distances = [
                self.roads[i].geom.distance(coord.geom)
                for i in nearest_candidates
            ]
            nearest_index = nearest_candidates[np.argmin(distances)]

        road = self.roads[nearest_index]

        return road

    def shortest_path(
        self,
        origin: Coordinate,
        destination: Coordinate,
        weight: PathWeight = PathWeight.TIME,
    ) -> List[Road]:
        """
        Computes the shortest path between an origin and a destination

        Args:
            origin: The origin coordinate
            destination: The destination coordinate
            weight: The weight to use for the path

        Returns:
            A list of roads that form the shortest path
        """
        if origin.crs != self.crs:
            raise ValueError(
                f"crs of origin {origin.crs} must match crs of map {self.crs}"
            )
        elif destination.crs != self.crs:
            raise ValueError(
                f"crs of destination {destination.crs} must match crs of map {self.crs}"
            )

        origin_road = self.nearest_road(origin)
        dest_road = self.nearest_road(destination)

        ostart = Point(origin_road.geom.coords[0])
        oend = Point(origin_road.geom.coords[-1])

        dstart = Point(dest_road.geom.coords[0])
        dend = Point(dest_road.geom.coords[-1])

        u_dist = ostart.distance(origin.geom)
        v_dist = oend.distance(origin.geom)

        if u_dist <= v_dist:
            origin_id = origin_road.origin_junction_id
        else:
            origin_id = origin_road.dest_junction_id

        u_dist = dstart.distance(destination.geom)
        v_dist = dend.distance(destination.geom)

        if u_dist <= v_dist:
            dest_id = dest_road.origin_junction_id
        else:
            dest_id = dest_road.dest_junction_id

        if weight == PathWeight.DISTANCE:
            weight_string = self._dist_weight
        elif weight == PathWeight.TIME:
            weight_string = self._time_weight
        else:
            raise TypeError(
                f"path weight {weight.name} is not supported by the NxMap"
            )

        nx_route = nx.shortest_path(
            self.g,
            origin_id,
            dest_id,
            weight=weight_string,
        )

        path = []
        for i in range(1, len(nx_route)):
            road_start_node = nx_route[i - 1]
            road_end_node = nx_route[i]

            edge_data = self.g.get_edge_data(road_start_node, road_end_node)

            road_key = list(edge_data.keys())[0]

            geom = edge_data[road_key][self._geom_key]
            road_id = edge_data[road_key][self._road_id_key]
            metadata = edge_data[road_key].get(self._metadata_key)

            path.append(
                Road(
                    road_id,
                    geom,
                    origin_junction_id=road_start_node,
                    dest_junction_id=road_end_node,
                    metadata=metadata,
                )
            )

        return path


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
