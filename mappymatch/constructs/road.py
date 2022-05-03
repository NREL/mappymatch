from __future__ import annotations

from typing import NamedTuple, Optional, Union

from shapely.geometry import LineString


class Road(NamedTuple):
    road_id: Union[int, str]

    geom: LineString
    origin_junction_id: Union[int, str]  # The id of the previous road in the path
    dest_junction_id: Union[int, str]  # The id of the next road in the path
    # holds any info specific to the road network
    metadata: Optional[dict] = None
