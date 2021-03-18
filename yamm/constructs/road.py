from __future__ import annotations
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from yamm.constructs.coordinate import Coordinate


class Road(NamedTuple):
    road_id: str

    start: Coordinate
    end: Coordinate
