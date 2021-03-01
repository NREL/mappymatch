from typing import NamedTuple

from yamm.constructs.coordinate import Coordinate


class Road(NamedTuple):
    road_id: str

    start: Coordinate
    end: Coordinate
