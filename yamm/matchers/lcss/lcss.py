import functools as ft

import logging
from multiprocessing import Pool
from typing import Optional

from yamm.maps.map_interface import MapInterface
from yamm.matchers.lcss.constructs import TrajectorySegment
from yamm.matchers.lcss.ops import new_path, split_trajectory_segment, same_trajectory_scheme, remove_bad_points
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
            road_map: MapInterface,
            distance_epsilon: float = 50.0,
            similarity_cutoff: float = 0.9,
            cutting_threshold: float = 10.0,
            random_cuts: int = 0,
            distance_threshold: float = 3000,
    ):
        self.map = road_map
        self.distance_epsilon = distance_epsilon
        self.similarity_cutoff = similarity_cutoff
        self.cutting_threshold = cutting_threshold
        self.random_cuts = random_cuts
        self.distance_threshold = distance_threshold

    def match_trace(self, trace: Trace, road_map: Optional[MapInterface] = None) -> MatchResult:
        if not road_map:
            road_map = self.map

        # bad_points_i, sub_trace = remove_bad_points(trace, road_map, distance_threshold=self.distance_threshold)
        #
        # if bad_points_i:
        #     log.warning(f"removed {len(bad_points_i)} from the trace for falling outside the road network")

        de = self.distance_epsilon
        ct = self.cutting_threshold
        rc = self.random_cuts
        initial_segment = TrajectorySegment(
            trace=trace,
            path=new_path(road_map, trace, de)
        ).score_and_match(de).compute_cutting_points(de, ct, rc)

        initial_scheme = split_trajectory_segment(road_map, initial_segment, de)
        scheme = initial_scheme

        n = 0
        while n < 10:
            next_scheme = []
            for segment in scheme:
                scored_segment = segment.score_and_match(de).compute_cutting_points(de, ct, rc)
                if scored_segment.score >= self.similarity_cutoff:
                    next_scheme.append(scored_segment)
                else:
                    # split and check the score
                    new_split = split_trajectory_segment(road_map, scored_segment, de)
                    joined_segment = ft.reduce(lambda acc, x: acc + x, new_split).score_and_match(de)
                    if joined_segment.score > scored_segment.score:
                        # we found a better fit
                        next_scheme.extend(new_split)
                    else:
                        next_scheme.append(scored_segment)
            n += 1
            if same_trajectory_scheme(scheme, next_scheme):
                break

            scheme = next_scheme

        joined_segment = ft.reduce(lambda acc, x: acc + x, scheme).score_and_match(de)

        return joined_segment.matches

    def match_trace_batch(
            self,
            trace_batch: List[Trace],
            processes: int = 1,
    ) -> List[MatchResult]:
        if processes > 1:
            results = [self.match_trace(t) for t in trace_batch]
        else:
            with Pool(processes=processes) as p:
                results = p.map(self.match_trace, trace_batch)

        return results
