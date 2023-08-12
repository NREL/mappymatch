from __future__ import annotations

from typing import Any, Dict, NamedTuple, Optional, Union

from shapely.geometry import LineString


class RoadId(NamedTuple):
    start: Union[int, str]
    end: Union[int, str]
    key: Union[int, str]

    def to_string(self) -> str:
        return f"{self.start},{self.end},{self.key}"

    def to_json(self) -> Dict[str, Any]:
        return self._asdict()

    @classmethod
    def from_string(cls, s: str) -> RoadId:
        start, end, key = s.split(",")
        return cls(start, end, key)

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> RoadId:
        return cls(**json)


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

    road_id: RoadId

    geom: LineString
    metadata: Optional[dict] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the road to a dictionary
        """
        d = self._asdict()
        d["origin_junction_id"] = self.road_id.start
        d["destination_junction_id"] = self.road_id.end
        d["road_key"] = self.road_id.key

        return d

    def to_flat_dict(self) -> Dict[str, Any]:
        """
        Convert the road to a flat dictionary
        """
        if self.metadata is None:
            return self.to_dict()
        else:
            d = {**self.to_dict(), **self.metadata}
            del d["metadata"]
            return d
