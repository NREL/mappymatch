import math

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.road import Road


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
