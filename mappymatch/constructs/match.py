from typing import NamedTuple, Optional

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.road import Road


class Match(NamedTuple):
    """
    Represents a match made by a Matcher

    Attributes:
        road: The road that was matched; None if no road was found;
        coordinate: The original coordinate that was matched;
        distance: The distance to the matched road; If no road was found, this is infinite
    """

    road: Optional[Road]
    coordinate: Coordinate
    distance: float

    def set_coordinate(self, c: Coordinate):
        """
        Set the coordinate of this match

        Args:
            c: The new coordinate

        Returns:
           The match with the new coordinate
        """
        return self._replace(coordinate=c)

    def to_flat_dict(self) -> dict:
        """
        Convert this match to a flat dictionary

        Returns:
            A flat dictionary with all match information
        """
        out = {"coordinate_id": self.coordinate.coordinate_id}

        if self.road is None:
            out["road_id"] = None
            return out
        else:
            out["distance_to_road"] = self.distance
            road_dict = self.road.to_flat_dict()
            out.update(road_dict)
            return out
