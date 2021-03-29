from typing import NamedTuple

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.road import Road


class Match(NamedTuple):
    """
    represents a match made by a map matching algorithm
    """
    road: Road
    coordinate: Coordinate
    distance: float

    def to_json(self) -> dict:
        out = {
            'road_id': self.road.road_id,
            'point_x': self.coordinate.x,
            'point_y': self.coordinate.y,
            'distance': self.distance
        }
        return out
