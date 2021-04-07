from pathlib import Path
from typing import List, Optional, Union

import networkx as nx
import rtree
from shapely.geometry import LineString
from sqlalchemy.future import Engine

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.constructs.road import Road
from yamm.maps.map_interface import MapInterface
from yamm.utils.crs import LATLON_CRS
from yamm.utils.tomtom import (
    get_tomtom_gdf,
    tomtom_gdf_to_nx_graph
)


class TomTomMap(MapInterface):
    DISTANCE_WEIGHT = "meters"
    TIME_WEIGHT = "minutes"
    SEARCH_BOX_SIZE = 200  # meters

    def __init__(self, graph: nx.MultiDiGraph):
        self.g = graph

        self._nodes = [nid for nid in self.g.nodes()]
        self.rtree = self._build_rtree()

    def _build_rtree(self) -> rtree.Index:
        items = []

        for i, gtuple in enumerate(self.g.edges(data=True, keys=True)):
            u, v, k, d = gtuple
            rid = (u, v, k)
            geom = d['geom']
            segment = list(geom.coords)
            box = geom.bounds
            items.append((i, box, (rid, segment)))

        return rtree.index.Index(items)

    @classmethod
    def from_file(cls, file: Union[str, Path]):
        """
        Build a NetworkXMap instance from a file

        :param file: the graph pickle file to load

        :return: a NetworkXMap instance
        """
        p = Path(file)
        if not p.suffix == ".pickle":
            raise TypeError(f"TomTomMap only supports pickle files")

        g = nx.read_gpickle(file)

        return TomTomMap(g)

    @classmethod
    def from_sql(cls, sql_connection: Engine, geofence: Geofence):
        """
        Loads a network from a sql database using the bounding box.

        :param sql_connection: the sql connection to build the network from.
        :param geofence: the boundary to specify what subset of the network to download.

        :return: a NetworkXMap instance
        """
        if geofence.crs != LATLON_CRS:
            raise TypeError(f"the geofence must in the epsg:4326 crs but got {geofence.crs.to_authority()}")
        gdf = get_tomtom_gdf(sql_connection, geofence)
        g = tomtom_gdf_to_nx_graph(gdf)

        return TomTomMap(g)

    def to_file(self, outfile: str):
        nx.write_gpickle(self.g, outfile)

    @property
    def roads(self) -> List[Road]:
        """
        returns the roads in the graph.

        :return:
        """
        roads = []
        for u, v, k, d in self.g.edges(data=True, keys=True):
            roads.append(Road(
                road_id=k,
                geom=d['geom'],
                metadata={'u': u, 'v': v},
            ))

        return roads

    def nearest_roads(
            self,
            coord: Coordinate,
            k: int = 1,
            search_size: float = 200,
    ) -> List[Road]:
        """
        a helper function to get the nearest road.

        :param coord:
        :param k: how many roads to return
        :param search_size: how far to search for a road

        :return:
        """

        def _find_roads(box_size):
            pbox = (coord.x - box_size, coord.y - box_size, coord.x + box_size, coord.y + box_size)
            hits = self.rtree.intersection(pbox, objects="raw")

            roads_w_dist = []

            for h in hits:
                u, v, rid = h[0]
                coords = h[1]
                line = LineString(coords)
                dist = coord.geom.distance(line)
                roads_w_dist.append((dist, Road(rid, line, metadata={'u': u, 'v': v})))

            sorted_roads = list(sorted(roads_w_dist, key=lambda t: t[0]))

            roads = list(map(lambda t: t[1], sorted_roads))
            return roads

        roads = _find_roads(search_size)
        attempts = 0
        while len(roads) < 1 and attempts < 10:
            # if we don't find any roads nearby, we'll double our search size
            search_size = search_size * 2
            roads = _find_roads(search_size)
            attempts += 1

        if len(roads) < 1:
            # todo: maybe we return an empty list and then the matcher can add a 'no-match' entry for the point
            raise Exception(f"could not find a matching road within {search_size} meters; check the road network")

        if k > len(roads):
            k = len(roads)

        return roads[:k]

    def shortest_path(self, origin: Coordinate, destination: Coordinate, weight: Optional[str] = None) -> List[Road]:
        """
        computes the shortest path between an origin and a destination

        :param origin:
        :param destination:
        :param weight:
        :return:
        """
        origin_road = self.nearest_roads(origin)[0]
        dest_road = self.nearest_roads(destination)[0]

        origin_id = origin_road.metadata['u']
        dest_id = dest_road.metadata['v']

        if not weight:
            weight = self.TIME_WEIGHT

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

            geom = edge_data[road_key]['geom']

            path.append(Road(road_key, geom, metadata={'u': road_start_node, 'v': road_end_node}))

        return path
