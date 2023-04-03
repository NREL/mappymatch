from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import networkx as nx
import numpy as np
import rtree as rt
import shapely.wkt as wkt
from shapely.geometry import Point

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.road import Road, RoadId
from mappymatch.maps.map_interface import (
    DEFAULT_DISTANCE_WEIGHT,
    DEFAULT_TIME_WEIGHT,
    MapInterface,
)
from mappymatch.maps.nx.readers.osm_readers import (
    NetworkType,
    nx_graph_from_osmnx,
)
from mappymatch.utils.crs import CRS, LATLON_CRS

DEFAULT_GEOMETRY_KEY = "geometry"
DEFAULT_METADATA_KEY = "metadata"
DEFAULT_CRS_KEY = "crs"


class NxMap(MapInterface):
    """
    A road map that uses a networkx graph to represent its roads.

    Attributes:
        g: The networkx graph that represents the road map
        crs: The coordinate reference system of the map
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.g = graph

        crs_key = graph.graph.get("crs_key", DEFAULT_CRS_KEY)

        if crs_key not in graph.graph:
            raise ValueError(
                "Input graph must have pyproj crs;"
                "You can set it like: `graph.graph['crs'] = pyproj.CRS('EPSG:4326')`"
            )

        crs = graph.graph[crs_key]

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
        self._crs_key = crs_key

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

    @property
    def distance_weight(self) -> str:
        return self._dist_weight

    @property
    def time_weight(self) -> str:
        return self._time_weight

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
        nx.set_edge_attributes(self.g, attributes)
        self._build_rtree()

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
        if p.suffix == ".pickle":
            g = nx.readwrite.read_gpickle(file)
            return NxMap(g)
        elif p.suffix == ".json":
            with p.open("r") as f:
                return NxMap.from_dict(json.load(f))
        else:
            raise TypeError("NxMap only supports pickle and json files")

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
        outfile = Path(outfile)

        if outfile.suffix == ".pickle":
            nx.write_gpickle(self.g, str(outfile))
        elif outfile.suffix == ".json":
            graph_dict = self.to_dict()
            with open(outfile, "w") as f:
                json.dump(graph_dict, f)
        else:
            raise TypeError(
                "NxMap only supports writing to pickle and json files"
            )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> NxMap:
        """
        Build a NxMap instance from a dictionary
        """
        for link in d["links"]:
            geom_wkt = link["geom"]
            link["geom"] = wkt.loads(geom_wkt)

        crs_key = d["graph"].get("crs_key", DEFAULT_CRS_KEY)
        crs = CRS.from_wkt(d["graph"][crs_key])
        d["graph"][crs_key] = crs

        g = nx.readwrite.json_graph.node_link_graph(d)

        return NxMap(g)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the map to a dictionary
        """
        graph_dict = nx.readwrite.json_graph.node_link_data(self.g)

        # convert geometries to well know text
        for link in graph_dict["links"]:
            geom = link["geom"]
            link["geom"] = geom.wkt

        # convert crs to well known text
        crs_key = graph_dict["graph"].get("crs_key", DEFAULT_CRS_KEY)
        graph_dict["graph"][crs_key] = self.crs.to_wkt()

        return graph_dict

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
        weight: Union[str, Callable] = DEFAULT_TIME_WEIGHT,
    ) -> List[Road]:
        """
        Computes the shortest path between an origin and a destination

        Args:
            origin: The origin coordinate
            destination: The destination coordinate
            weight: The weight to use for the path, either a string or a function

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

        nx_route = nx.shortest_path(
            self.g,
            origin_id,
            dest_id,
            weight=weight,
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
