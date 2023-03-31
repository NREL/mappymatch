from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import networkx as nx
import numpy as np
import rtree as rt
from shapely.geometry import Point

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.road import Road, RoadId
from mappymatch.maps.map_interface import MapInterface, PathWeight
from mappymatch.maps.nx.readers.osm_readers import (
    NetworkType,
    nx_graph_from_osmnx,
)
from mappymatch.utils.crs import CRS, LATLON_CRS

DEFAULT_DISTANCE_WEIGHT = "kilometers"
DEFAULT_TIME_WEIGHT = "minutes"
DEFAULT_GEOMETRY_KEY = "geometry"


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
        metadata_key = graph.graph.get("metadata_key", DEFAULT_METADATA_KEY)

        self._dist_weight = dist_weight
        self._time_weight = time_weight
        self._geom_key = geom_key
        self._metadata_key = metadata_key

        self._build_rtree()

    def _build_road(
        self,
        origin_id: Union[str, int],
        destination_id: Union[str, int],
        key: Union[str, int],
        edge_data: Dict[str, Any],
    ) -> Road:
        """
        Build a road from an origin, destination and networkx edge data
        """
        metadata = edge_data.get(self._metadata_key)

        if metadata is None:
            metadata = {}
        else:
            metadata = metadata.copy()

        metadata[self._dist_weight] = edge_data.get(self._dist_weight)
        metadata[self._time_weight] = edge_data.get(self._time_weight)

        road_id = RoadId(origin_id, destination_id, key)

        road = Road(
            road_id,
            edge_data[self._geom_key],
            metadata=metadata,
        )

        return road

    def _build_rtree(self):
        road_lookup = {}

        idx = rt.index.Index()
        for i, gtuple in enumerate(self.g.edges(data=True, keys=True)):
            u, v, k, d = gtuple
            road = self._build_road(u, v, k, d)
            geom = d[self._geom_key]
            box = geom.bounds

            idx.insert(i, box, obj=road.road_id)

            road_lookup[road.road_id] = road

        self.rtree = idx
        self._road_lookup: Dict[RoadId, Road] = road_lookup

    def __str__(self):
        output_lines = [
            "Mappymatch NxMap object",
            f"roads: {len(self._road_lookup)} Road objects",
            f"graph: {self.g}",
        ]
        return "\n".join(output_lines)

    def __repr__(self):
        return self.__str__()

    def road_by_id(self, road_id: RoadId) -> Optional[Road]:
        """
        Get a road by its id

        Args:
            road_id: The id of the road to get

        Returns:
            The road with the given id, or None if it does not exist
        """
        return self._road_lookup.get(road_id)

    def set_road_attributes(self, attributes: Dict[RoadId, Dict[str, Any]]):
        """
        Set the attributes of the roads in the map

        Args:
            attributes: A dictionary mapping road ids to dictionaries of attributes

        Returns:
            None
        """
        return None

    @property
    def roads(self) -> List[Road]:
        return list(self._road_lookup.values())

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

        nx_graph = nx_graph_from_osmnx(
            geofence=geofence, network_type=network_type, xy=xy
        )

        return NxMap(nx_graph)

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
            map(
                lambda c: c.object,
                (
                    self.rtree.nearest(
                        coord.geom.buffer(buffer).bounds, 1, objects=True
                    )
                ),
            )
        )

        if len(nearest_candidates) == 0:
            raise ValueError(f"No roads found for {coord}")
        elif len(nearest_candidates) == 1:
            nearest_id = nearest_candidates[0]
        else:
            distances = [
                self._road_lookup[i].geom.distance(coord.geom)
                for i in nearest_candidates
            ]
            nearest_id = nearest_candidates[np.argmin(distances)]

        road = self._road_lookup[nearest_id]

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
            origin_id = origin_road.road_id.start
        else:
            origin_id = origin_road.road_id.end

        u_dist = dstart.distance(destination.geom)
        v_dist = dend.distance(destination.geom)

        if u_dist <= v_dist:
            dest_id = dest_road.road_id.start
        else:
            dest_id = dest_road.road_id.end

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

            road_id = RoadId(road_start_node, road_end_node, road_key)

            road = self._road_lookup[road_id]

            path.append(road)

        return path
