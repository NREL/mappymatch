from __future__ import annotations

from typing import Any, Dict, NamedTuple, Optional, Union

from shapely.geometry import LineString


class Road(NamedTuple):
    """
    Represents a road that can be matched to;

    Attributes:
        road_id: The unique identifier for this road
        geom: The geometry of this road
        origin_junction_id: The unique identifier of the origin junction of this road
        destination_junction_id: The unique identifier of the destination junction of this road
        metadata: an optional dictionary for storing additional metadata
    """

    road_id: Union[int, str]

    geom: LineString
    origin_junction_id: Optional[Union[int, str]] = None
    dest_junction_id: Optional[Union[int, str]] = None
    metadata: Optional[dict] = None

    def to_flat_dict(self) -> Dict[str, Any]:
        """
        Convert the road to a flat dictionary
        """
        if self.metadata is None:
            return self._asdict()
        else:
            d = {**self._asdict(), **self.metadata}
            del d["metadata"]
            return d
