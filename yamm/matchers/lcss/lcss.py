from yamm.maps.map_interface import MapInterface
from yamm.matchers.matcher_interface import *


class LCSSMatcher(MatcherInterface):
    """
    A map matcher based on the paper:

    Zhu, Lei, Jacob R. Holden, and Jeffrey D. Gonder.
    "Trajectory Segmentation Map-Matching Approach for Large-Scale, High-Resolution GPS Data."
    Transportation Research Record: Journal of the Transportation Research Board 2645 (2017): 67-75.

    """

    def __init__(
            self,
            road_map: MapInterface
    ):
        self.map = road_map

    def match_trace(self, trace: Trace) -> MatchResult:
        pass

    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
