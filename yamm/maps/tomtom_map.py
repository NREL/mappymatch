from functools import cached_property
from pathlib import Path
from typing import List, Union

import networkx as nx
from pygeos import STRtree, Geometry
from shapely.geometry import Point
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
        self._build_rtree()

    def _build_rtree(self):
        geoms = []
        road_lookup = []
        for u, v, rid, d, in self.g.edges(data=True, keys=True):
            geoms.append(Geometry(d['geom'].wkb))
            road = Road(rid, d['geom'], metadata={'u': u, 'v': v})
            road_lookup.append(road)

        self.rtree = STRtree(geoms)
        self.roads = road_lookup

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

    def nearest_road(
            self,
            coord: Coordinate,
    ) -> Road:
        """
        a helper function to get the nearest road.

        :param coord:

        :return:
        """
        nearest_index = self.rtree.nearest([Geometry(coord.geom.wkb)]).tolist()[-1][0]

        road = self.roads[nearest_index]

        return road

    def shortest_path(self, origin: Coordinate, destination: Coordinate, weight: PathWeight = PathWeight.TIME) -> List[
        Road]:
        """
        computes the shortest path between an origin and a destination

        :param origin:
        :param destination:
        :param weight:
        :return:
        """
        origin_road = self.nearest_road(origin)
        dest_road = self.nearest_road(destination)

        ostart, oend = origin_road.geom.boundary
        dstart, dend = dest_road.geom.boundary

        u_dist = ostart.distance(origin.geom)
        v_dist = oend.distance(origin.geom)

        if u_dist <= v_dist:
            origin_id = origin_road.metadata['u']
        else:
            origin_id = origin_road.metadata['v']

        u_dist = dstart.distance(destination.geom)
        v_dist = dend.distance(destination.geom)

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
