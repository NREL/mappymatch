from __future__ import annotations

from typing import NamedTuple

from shapely.geometry import LineString


class Road(NamedTuple):
    road_id: str

    geom: LineString
