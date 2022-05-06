from __future__ import annotations

from pathlib import Path
from typing import List, Union

import networkx as nx
import rtree as rt
from shapely.geometry import Point

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.road import Road
from mappymatch.maps.map_interface import MapInterface, PathWeight
from mappymatch.utils.crs import CRS

DEFAULT_DISTANCE_WEIGHT = "kilometers"
DEFAULT_TIME_WEIGHT = "minutes"
DEFAULT_GEOMETRY_KEY = "geometry"
DEFAULT_ROAD_ID_KEY = "road_id"


class NxMap(MapInterface):
    def __init__(self, graph: nx.MultiDiGraph):
        self.g = graph
        if not (crs := graph.graph.get("crs")):
            raise ValueError(
                "Input graph must have pyproj crs;"
                "You can set it like: `graph.graph['crs'] = pyproj.CRS('EPSG:4326')`"
            )

        if not isinstance(crs, CRS):
            raise TypeError(
                "Input graph must have pyproj crs;"
                "You can set it like: `graph.graph['crs'] = pyproj.CRS('EPSG:4326')`"
            )
        self.crs = crs

        self._dist_weight = graph.graph.get(
            "distance_weight", DEFAULT_DISTANCE_WEIGHT
        )
        self._time_weight = graph.graph.get("time_weight", DEFAULT_TIME_WEIGHT)
        self._geom_key = graph.graph.get("geometry_key", DEFAULT_GEOMETRY_KEY)
        self._road_id_key = graph.graph.get("road_id", DEFAULT_ROAD_ID_KEY)

        self._nodes = [nid for nid in self.g.nodes()]
        self._roads = self._build_rtree()

    def _build_rtree(self) -> List[Road]:
        def _inner_build_rtree():
            idx = rt.index.Index()
            for i, (u, v, k, d) in enumerate(
                self.g.edges(data=True, keys=True)
            ):
                idx.insert(i, d[self._geom_key].bounds)
                yield Road(
                    d[self._road_id_key],
                    d[self._geom_key],
                    origin_junction_id=u,
                    dest_junction_id=v,
                )

            self.rtree = idx

        return list(_inner_build_rtree())

    @property
    def roads(self) -> List[Road]:
        return self._roads

    @classmethod
    def from_file(cls, file: Union[str, Path]) -> NxMap:
        """
        Build a NxMap instance from a file

        :param file: the graph pickle file to load

        :return: a NxMap instance
        """
        p = Path(file)
        if not p.suffix == ".pickle":
            raise TypeError("NxMap only supports pickle files")

        g = nx.read_gpickle(file)

        return NxMap(g)

    def to_file(self, outfile: Union[str, Path]):
        nx.write_gpickle(self.g, str(outfile))

    def nearest_road(
        self,
        coord: Coordinate,
    ) -> Road:
        """
        a helper function to get the nearest road.

        :param coord:

        :return:
        """
        if coord.crs != self.crs:
            raise ValueError(
                f"crs of origin {coord.crs} must match crs of map {self.crs}"
            )
        try:
            return self.roads[next(self.rtree.nearest(coord.geom.bounds, 1))]
        except StopIteration:
            raise ValueError(f"No roads found for {coord}")

    def shortest_path(
        self,
        origin: Coordinate,
        destination: Coordinate,
        weight: PathWeight = PathWeight.TIME,
    ) -> List[Road]:
        """
        computes the shortest path between an origin and a destination

        :param origin:
        :param destination:
        :param weight:
        :return:
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

            road_key = next(edge_data.keys())

            geom = edge_data[road_key][self._geom_key]
            road_id = edge_data[road_key][self._road_id_key]

            path.append(
                Road(
                    road_id,
                    geom,
                    origin_junction_id=road_start_node,
                    dest_junction_id=road_end_node,
                )
            )

        return path
