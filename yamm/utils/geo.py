import math

import numpy as np
from shapely.geometry import box

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.constructs.road import Road
from yamm.constructs.trace import Trace
from yamm.utils.crs import XY_CRS


def compute_bounding_box(trace: Trace, padding: float = 0) -> Geofence:
    """
    computes a bounding box surrounding a trace by taking the minimum and maximum x and y

    :param trace: the trace to compute the bounding box for
    :param padding: how much padding (in meters) to add to the box

    :return: the computed bounding box
    """
    x = [c.x for c in trace.coords]
    y = [c.y for c in trace.coords]

    min_x = np.min(x) - padding
    min_y = np.min(y) - padding

    max_x = np.max(x) + padding
    max_y = np.max(y) + padding

    bbox = box(min_x, min_y, max_x, max_y)

    return Geofence(crs=XY_CRS, geometry=bbox)


def road_to_coord_dist(road: Road, coord: Coordinate) -> float:
    """
    helper function to compute the distance between a coordinate and a road

    :param road: the road object
    :param coord: the coordinate object

    :return: the distance
    """

    lx = road.end.x - road.start.x
    ly = road.end.y - road.start.y

    denom = max(lx * lx + ly * ly, 0.00000001)

    u = ((coord.x - road.start.x) * lx + (coord.y - road.start.y) * ly) / denom

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = road.start.x + u * lx
    y = road.start.y + u * ly

    dx = x - coord.x
    dy = y - coord.y

    dist = math.sqrt(dx * dx + dy * dy)

    return dist


def coord_to_coord_dist(a: Coordinate, b: Coordinate):
    """
    helper function to compute the distance between to coordinates

    :param a: coordinate a
    :param b: coordinate b

    :return: the distance
    """
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
