from typing import List, Optional, Union
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.spatial import cKDTree

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.road import Road
from yamm.maps.map_interface import MapInterface
from yamm.utils.geo import road_to_coord_dist


class NetworkXMap(MapInterface):
    DISTANCE_WEIGHT = "meters"
    TIME_WEIGHT = "minutes"

    def __init__(self, graph_file: Union[str, Path]):
        self.g = nx.read_gpickle(graph_file)

        self._nodes = [nid for nid in self.g.nodes()]
        self.kdtree = self._build_kdtree()

    def _build_kdtree(self) -> cKDTree:
        points = [(self.g.nodes[nid]['lat'], self.g.nodes[nid]['lon']) for nid in self._nodes]
        tree = cKDTree(np.array(points))

        return tree

    def _get_nearest_node(self, coord: Coordinate) -> str:
        _, i = self.kdtree.query([coord.lat, coord.lon])
        return self._nodes[i]

    @property
    def roads(self) -> List[Road]:
        """
        returns the roads in the graph.

        :return:
        """
        roads = []
        for u, v in self.g.edges():
            u_node = self.g.nodes[u]
            v_node = self.g.nodes[v]
            roads.append(Road(
                road_id=str((u, v)),
                start=Coordinate(lat=u_node['lat'], lon=u_node['lon'], x=u_node['x'], y=u_node['y']),
                end=Coordinate(lat=v_node['lat'], lon=v_node['lon'], x=v_node['x'], y=v_node['y']),
            ))

        return roads

    def nearest_road(self, coord: Coordinate) -> Road:
        """
        a helper function to get the nearest road.

        :param coord:
        :return:
        """
        nearest_node = self._get_nearest_node(coord)

        edges_to_consider = list(self.g.out_edges(nearest_node)) + list(self.g.in_edges(nearest_node))

        if not edges_to_consider:
            raise Exception("nearest node does not have any edges")

        roads = []
        for u, v in edges_to_consider:
            road = Road(
                road_id=str((u, v)),
                start=Coordinate(self.g.nodes[u]['lat'], self.g.nodes[u]['lon'], self.g.nodes[u]['x'],
                                 self.g.nodes[u]['y']),
                end=Coordinate(self.g.nodes[v]['lat'], self.g.nodes[v]['lon'], self.g.nodes[v]['x'],
                               self.g.nodes[v]['y']),
            )
            roads.append(road)

        i = np.argmin([road_to_coord_dist(r, coord) for r in roads])
        return roads[i]

    def shortest_path(self, origin: Coordinate, destination: Coordinate, weight: Optional[str] = None) -> List[Road]:
        """
        computes the shortest path between an origin and a destination

        :param origin:
        :param destination:
        :param weight:
        :return:
        """
        origin_id = self._get_nearest_node(origin)
        dest_id = self._get_nearest_node(destination)

        if not weight:
            weight = self.DISTANCE_WEIGHT

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
            road_id = f"({road_start_node},{road_end_node})"

            road_start_coord = Coordinate(
                lat=self.g.nodes[road_start_node]['lat'],
                lon=self.g.nodes[road_start_node]['lon'],
                x=self.g.nodes[road_start_node]['x'],
                y=self.g.nodes[road_start_node]['y'],
            )
            road_end_coord = Coordinate(
                lat=self.g.nodes[road_end_node]['lat'],
                lon=self.g.nodes[road_end_node]['lon'],
                x=self.g.nodes[road_end_node]['x'],
                y=self.g.nodes[road_end_node]['y'],
            )

            path.append(Road(road_id, road_start_coord, road_end_coord))

        return path
