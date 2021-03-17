from typing import NamedTuple

from yamm.constructs.coordinate import Coordinate


class BoundingBox(NamedTuple):
    southwest_corner: Coordinate
    northeast_corner: Coordinate
