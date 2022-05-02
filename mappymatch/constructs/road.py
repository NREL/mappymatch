from __future__ import annotations

from typing import NamedTuple, Optional, Union

from shapely.geometry import LineString


class Road(NamedTuple):
    road_id: Union[int, str]

    geom: LineString

    # holds any info specific to the road network
    metadata: Optional[dict] = None
