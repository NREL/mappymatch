from __future__ import annotations

import logging
import random
from typing import NamedTuple, List

import numpy as np

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.match import Match
from yamm.constructs.road import Road
from yamm.constructs.trace import Trace
from yamm.matchers.lcss.utils import compress
from yamm.utils.geo import road_to_coord_dist, coord_to_coord_dist

log = logging.getLogger(__name__)


class CuttingPoint(NamedTuple):
    trace_index: int
    coordinate: Coordinate


class TrajectorySegment(NamedTuple):
    """
    represents a trace and path matching
    """
    trace: Trace
    path: List[Road]

    matches: List[Match] = []

    score: float = 0

    cutting_points: List[CuttingPoint] = []

    def __add__(self, other):
        new_traces = self.trace + other.trace
        new_paths = self.path + other.path
        return TrajectorySegment(new_traces, new_paths)

    def set_score(self, score: float):
        return self._replace(score=score)

    def set_cutting_points(self, cutting_points):
        return self._replace(cutting_points=cutting_points)

    def set_matches(self, matches):
        return self._replace(matches=matches)

    def score_and_match(self, distance_epsilon: float) -> TrajectorySegment:
        """
        computes the score of a trace, pair matching and also matches the coordinates to the nearest road.

        :param distance_epsilon
        
        return: updated trajectory segment with a score and matched points
        """
        trace = self.trace
        path = self.path

        m = len(trace.coords)
        n = len(path)

        matched_roads = []

        if m < 10:
            # todo: find a better way to handle this edge case
            raise Exception(f"traces of less than 10 points can't be matched")
        elif n < 2:
            # this likely means the trace starts and ends at the same point;
            return self.set_score(0)

        C = [[0 for i in range(n + 1)] for j in range(m + 1)]

        for i in range(1, m + 1):
            nearest_road = None
            min_dist = np.inf
            coord = trace.coords[i - 1]
            for j in range(1, n + 1):
                road = path[j - 1]

                dt = road_to_coord_dist(road, coord)

                if dt < min_dist:
                    min_dist = dt
                    nearest_road = road

                if dt < distance_epsilon:
                    point_similarity = 1 - (dt / distance_epsilon)
                else:
                    point_similarity = 0

                C[i][j] = max((C[i - 1][j - 1] + point_similarity), C[i][j - 1], C[i - 1][j])

            if not nearest_road:
                # todo: maybe we just return None?
                raise Exception(f"could not find nearest road for coord {coord}")

            match = Match(
                road=nearest_road,
                distance=min_dist,
                coordinate=coord,
            )
            matched_roads.append(match)

        sim_score = C[m][n] / float(min(m, n))

        return self.set_score(sim_score).set_matches(matched_roads)

    def compute_cutting_points(
            self,
            distance_epsilon: float,
            cutting_thresh: float,
            random_cuts: int,
    ) -> TrajectorySegment:
        """
        Computes the cutting points for a trajectory segment by:
         - computing the furthest point 
         - adding points that are close to the distance epsilon

        :param distance_epsilon:
        :param cutting_thresh:
        :param random_cuts:

        :return: the updated trajectory segment with cutting points 
        """
        cutting_points = []

        if not self.matches:
            # no matches computed, let's just split the trajectory based on the furthest points
            start = self.trace.coords[0]
            end = self.trace.coords[-1]
            p1 = np.argmax([coord_to_coord_dist(start, c) for c in self.trace.coords])
            p2 = np.argmax([coord_to_coord_dist(end, c) for c in self.trace.coords])

            cp1 = CuttingPoint(p1, self.trace.coords[p1])
            cp2 = CuttingPoint(p2, self.trace.coords[p2])
            return self.set_cutting_points([cp1, cp2])

        # find furthest point
        i = np.argmax([m.distance for m in self.matches])
        cutting_points.append(CuttingPoint(i, self.trace.coords[i]))

        # collect points that are close to the distance threshold
        for i, m in enumerate(self.matches):
            if abs(m.distance - distance_epsilon) < cutting_thresh:
                cutting_points.append(CuttingPoint(i, self.trace.coords[i]))

        # add random points
        for _ in range(random_cuts):
            cpi = random.randint(0, len(self.trace)-1)
            cutting_points.append(CuttingPoint(cpi, self.trace.coords[i]))

        compressed_cuts = list(compress(cutting_points))

        return self.set_cutting_points(compressed_cuts)


TrajectoryScheme = List[TrajectorySegment]
