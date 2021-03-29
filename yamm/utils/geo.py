from typing import Tuple

import numpy as np
from pyproj import Transformer
from rtree import index
from shapely.geometry import box

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.constructs.road import Road
from yamm.constructs.trace import Trace
from yamm.maps.map_interface import MapInterface
from yamm.utils.crs import XY_CRS, LATLON_CRS


def build_rtree(road_map: MapInterface):
    """
    builds an rtree index from a map connection.
    """
    items = []

    for i, road in enumerate(road_map.roads):
        rid = road.road_id
        segment = list(road.geom.coords)
        box = road.geom.bounds
        items.append((i, box, (rid, segment)))
    return index.Index(items)


def xy_to_latlon(x: float, y: float) -> Tuple[float, float]:
    transformer = Transformer.from_crs(XY_CRS, LATLON_CRS)
    lat, lon = transformer.transform(x, y)

    return lat, lon


def latlon_to_xy(lat: float, lon: float) -> Tuple[float, float]:
    transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)
    x, y = transformer.transform(lat, lon)

    return x, y


def geofence_from_trace(trace: Trace, padding: float = 0, xy: bool = False) -> Geofence:
    """
    computes a bounding box surrounding a trace by taking the minimum and maximum x and y

    :param trace: the trace to compute the bounding box for
    :param padding: how much padding (in meters) to add to the box
    :param xy: should the geofence be projected to xy?

    :return: the computed bounding box
    """
    x = [c.x for c in trace.coords]
    y = [c.y for c in trace.coords]

    min_x = np.min(x) - padding
    min_y = np.min(y) - padding

    max_x = np.max(x) + padding
    max_y = np.max(y) + padding

    if xy:
        bbox = box(min_x, min_y, max_x, max_y)
        return Geofence(crs=XY_CRS, geometry=bbox)

    min_lat, min_lon = xy_to_latlon(min_x, min_y)
    max_lat, max_lon = xy_to_latlon(max_x, max_y)

    bbox = box(min_lon, min_lat, max_lon, max_lat)

    return Geofence(crs=LATLON_CRS, geometry=bbox)


def road_to_coord_dist(road: Road, coord: Coordinate) -> float:
    """
    helper function to compute the distance between a coordinate and a road

    :param road: the road object
    :param coord: the coordinate object

    :return: the distance
    """

    dist = coord.geom.distance(road.geom)

    return dist


def coord_to_coord_dist(a: Coordinate, b: Coordinate):
    """
    helper function to compute the distance between to coordinates

    :param a: coordinate a
    :param b: coordinate b

    :return: the distance
    """
    dist = a.geom.distance(b.geom)

    return dist
