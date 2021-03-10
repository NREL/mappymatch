import functools as ft

import logging

from yamm.maps.map_interface import MapInterface
from yamm.matchers.lcss.constructs import TrajectorySegment
from yamm.matchers.lcss.ops import new_path, split_trajectory_segment, same_trajectory_scheme
from yamm.matchers.matcher_interface import *

log = logging.getLogger(__name__)


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
        initial_segment = TrajectorySegment(
            trace=trace,
            path=new_path(self.map, trace)
        ).score_and_match().compute_cutting_points()

        initial_scheme = split_trajectory_segment(self.map, initial_segment)

        scheme = initial_scheme

        n = 0
        while n < 10:
            next_scheme = []
            for segment in scheme:
                scored_segment = segment.score_and_match().compute_cutting_points()
                if scored_segment.similar:
                    next_scheme.append(scored_segment)
                else:
                    # split and check the score
                    new_split = split_trajectory_segment(self.map, scored_segment)
                    joined_segment = ft.reduce(lambda acc, x: acc + x, new_split).score_and_match()
                    if joined_segment.score > scored_segment.score:
                        # we found a better fit
                        next_scheme.extend(new_split)
                    else:
                        next_scheme.append(scored_segment)
            n += 1
            if same_trajectory_scheme(scheme, next_scheme):
                break

            scheme = next_scheme

        joined_segment = ft.reduce(lambda acc, x: acc + x, scheme).score_and_match()

        # todo: only return the matches
        return joined_segment.matches

    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
