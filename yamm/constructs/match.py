from typing import NamedTuple

from yamm.constructs.coordinate import Coordinate


class Match(NamedTuple):
    """
    represents a match made by a map matching algorithm
    """
    road_id: str
    coordinate: Coordinate
    distance: float
