from typing import List

import networkx as nx

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.road import Road
from yamm.maps.map_interface import MapInterface


class NetworkXMap(MapInterface):

    def __init__(self, graph_file: str):
        self.g = nx.read_gpickle(graph_file)

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

