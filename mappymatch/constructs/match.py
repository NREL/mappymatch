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

    def to_json(self) -> dict:
        """
        Convert this match to a json object

        Returns:
            A json object representing this match
        """
        out = {
            "road_id": self.road.road_id if self.road else None,
            "coordinate_id": self.coordinate.coordinate_id,
            "distance_to_road": self.distance,
        }
        return out
