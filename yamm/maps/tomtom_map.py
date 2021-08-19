from pathlib import Path
from typing import List, Union

import networkx as nx
import rtree
from shapely.geometry import LineString, Point
from sqlalchemy.future import Engine

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.constructs.road import Road
from yamm.maps.map_interface import MapInterface, PathWeight
from yamm.utils.crs import LATLON_CRS
from yamm.utils.tomtom import (
    get_tomtom_gdf,
    tomtom_gdf_to_nx_graph
)


class TomTomMap(MapInterface):
    DISTANCE_WEIGHT = "kilometers"
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

    def to_file(self, outfile: Union[str, Path]):
        nx.write_gpickle(self.g, str(outfile))

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

    def coordinate_outside_boundary(self, coord: Coordinate, max_distance: float = 3000) -> bool:
        """
        test if there is a road within the max distance

        :param coord:
        :param max_distance:

        :return:
        """
        pbox = (coord.x - max_distance, coord.y - max_distance, coord.x + max_distance, coord.y + max_distance)
        hits = self.rtree.intersection(pbox, objects="raw")

        try:
            _ = next(hits)
            # if there is a hit we're not outside the boundary
            return False
        except StopIteration:
            # no hits so we're outside the boundary
            return True

    def nearest_roads(
            self,
            coord: Coordinate,
            k: int = 1,
            search_size: float = 200,
            max_distance: float = 3000,
    ) -> List[Road]:
        """
        a helper function to get the nearest road.

        :param coord:
        :param k: how many roads to return
        :param search_size: distance in meters used to construct search bounding box
        :param max_distance: maximum distance to search for

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
        while len(roads) < 1 and search_size <= max_distance:
            # if we don't find any roads nearby, we'll double our search size
            search_size = search_size * 2
            roads = _find_roads(search_size)
            attempts += 1

        if len(roads) < 1:
            raise Exception(f"could not find a matching road within {search_size} meters; check the road network")

        if k > len(roads):
            k = len(roads)

        return roads[:k]

    def shortest_path(self, origin: Coordinate, destination: Coordinate, weight: PathWeight = PathWeight.TIME) -> List[
        Road]:
        """
        computes the shortest path between an origin and a destination

        :param origin:
        :param destination:
        :param weight:
        :return:
        """
        origin_roads = self.nearest_roads(origin)
        dest_roads = self.nearest_roads(destination)

        if len(origin_roads) == 0:
            return []
        else:
            origin_road = origin_roads[0]

        if len(dest_roads) == 0:
            return []
        else:
            dest_road = dest_roads[0]

        u_dist = Point(origin_road.geom.coords[0]).distance(origin.geom)
        v_dist = Point(origin_road.geom.coords[-1]).distance(origin.geom)

        if u_dist <= v_dist:
            origin_id = origin_road.metadata['u']
        else:
            origin_id = origin_road.metadata['v']

        u_dist = Point(dest_road.geom.coords[0]).distance(destination.geom)
        v_dist = Point(dest_road.geom.coords[-1]).distance(destination.geom)

        if u_dist <= v_dist:
            dest_id = dest_road.metadata['u']
        else:
            dest_id = dest_road.metadata['v']

        if weight == PathWeight.DISTANCE:
            weight_string = self.DISTANCE_WEIGHT
        elif weight == PathWeight.TIME:
            weight_string = self.TIME_WEIGHT
        else:
            raise TypeError(f"path weight {weight.name} is not supported by the TomTomMap")

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

            geom = edge_data[road_key]['geom']

            path.append(Road(road_key, geom, metadata={'u': road_start_node, 'v': road_end_node}))

        return path
