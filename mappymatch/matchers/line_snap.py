import logging
from typing import List

from mappymatch.constructs.match import Match
from mappymatch.constructs.trace import Trace
from mappymatch.maps.map_interface import MapInterface
from mappymatch.matchers.matcher_interface import MatcherInterface, MatchResult

log = logging.getLogger(__name__)


class LineSnapMatcher(MatcherInterface):
    """
    A crude (but fast) map matcher that just snaps points to the nearest road network link.

    Attributes:
        map: The map to match against
    """

    def __init__(self, road_map: MapInterface):
        self.map = road_map

    def match_trace(self, trace: Trace) -> MatchResult:
        matches = []

        for coord in trace.coords:
            nearest_road = self.map.nearest_road(coord)
            nearest_point = nearest_road.geom.interpolate(
                nearest_road.geom.project(coord.geom)
            )
            dist = nearest_road.geom.distance(nearest_point)
            match = Match(nearest_road, coord, dist)
            matches.append(match)

        return MatchResult(matches)

    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
