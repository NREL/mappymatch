from typing import NamedTuple, List

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.match import Match
from yamm.constructs.trace import Trace
from yamm.maps.networkx_map import Path


class CuttingPoint(NamedTuple):
    trace_index: int
    coordinate: Coordinate


class TrajectorySegment(NamedTuple):
    """
    represents a trace and path matching
    """
    trace: Trace
    path: Path

    matches: List[Match] = []

    score: float = 0
    similar: bool = False

    cutting_points: List[Coordinate] = []

    def __add__(self, other):
        new_traces = self.trace + other.trace
        new_paths = self.path + other.path
        return TrajectorySegment(new_traces, new_paths)

    def set_score(self, score):
        if score > 0.9:
            similar = True
        else:
            similar = False

        return self._replace(score=score, similar=similar)

    def set_cutting_points(self, cutting_points):
        return self._replace(cutting_points=cutting_points)

    def set_matches(self, matches):
        return self._replace(matches=matches)


class ScoreResult(NamedTuple):
    trajectory_segment: TrajectorySegment
    cutting_points: List[Coordinate]
