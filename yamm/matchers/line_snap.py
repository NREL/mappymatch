import logging
import math
from typing import Tuple

import numpy as np
from rtree import index
from shapely.geometry import Point

from yamm.maps.map_interface import MapInterface
from yamm.matchers.matcher_interface import *

log = logging.getLogger(__name__)


def build_rtree(road_map: MapInterface):
    """
    builds an rtree index from a map connection.
    """
    items = []

    sindx = 0
    for road in road_map.roads:
        lid = road.road_id
        a = road.start.x
        b = road.start.y
        c = road.end.x
        d = road.end.y
        if not a or not b or not c or not d:
            raise ValueError(
                f"LineSnapMatcher requires projected x,y data but found a road without this information"
            )
        segment = ((a, b), (c, d))
        box = (min(a, c), min(b, d), max(a, c), max(b, d))
        items.append((sindx, box, (lid, segment)))
        sindx += 1
    return index.Index(items)


def distance(a: Point, b: Point):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def get_distance(point: Point, segment: Tuple[Point, Point]):
    a = point
    b = Point(segment[0].x, segment[0].y)
    c = Point(segment[1].x, segment[1].y)

    t = (a.x - b.x) * (c.x - b.x) + (a.y - b.y) * (c.y - b.y)
    try:
        t = t / ((c.x - b.x) ** 2 + (c.y - b.y) ** 2)
    except ZeroDivisionError:
        t = 1

    if 0 < t < 1:
        pcoords = Point(t * (c.x - b.x) + b.x, t * (c.y - b.y) + b.y)
        dmin = distance(a, pcoords)
        return dmin
    elif t <= 0:
        return distance(a, b)
    elif 1 <= t:
        return distance(a, c)


class LineSnapMatcher(MatcherInterface):
    """
    A crude (but fast) map matcher that just snaps points to the nearest road network link.
    """

    BOX_SIZE = 200  # meters

    def __init__(self, road_map: MapInterface):
        self.map = road_map
        self.rtree = build_rtree(road_map)

    def match_trace(self, trace: Trace) -> MatchResult:
        # Box size for searching rtree
        line_ids = []

        for coord in trace.coords:
            if not coord.x or not coord.y:
                raise ValueError(
                    "this trace requires projected x, y data but found a coordinate with only lat/lon"
                )
            p = Point(coord.x, coord.y)
            pbox = (
                coord.x - self.BOX_SIZE,
                coord.y - self.BOX_SIZE,
                coord.x + self.BOX_SIZE,
                coord.y + self.BOX_SIZE,
            )
            hits = self.rtree.intersection(pbox, objects="raw")
            d = np.inf
            s = None
            for h in hits:
                new_d = get_distance(p, (Point(h[1][0]), Point(h[1][1])))
                if d >= new_d:
                    d = new_d
                    s = (h[0], h[1])
            if not s:
                line_ids.append("UNABLE_TO_SNAP")
            else:
                line_ids.append(s[0])

        return line_ids

    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
