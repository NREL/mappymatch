import logging
import time
from copy import deepcopy
from typing import Any, List, NamedTuple

import numpy as np

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.road import Road
from mappymatch.constructs.trace import Trace
from mappymatch.maps.map_interface import MapInterface, PathWeight
from mappymatch.matchers.lcss.constructs import (
    TrajectoryScheme,
    TrajectorySegment,
)
from mappymatch.matchers.lcss.utils import merge
from mappymatch.matchers.matcher_interface import MatchResult

log = logging.getLogger(__name__)


def score(trace: Trace, path: List[Road], distance_epsilon: float) -> float:
    """
    Computes the similarity score between a trace and a path

    Args:
        trace: the trace to compare
        path: the path to compare
        distance_epsilon: the distance epsilon

    Returns:
        the similarity score
    """
    s = time.time()
    m = len(trace.coords)
    n = len(path)

    if m < 2:
        return 0
    elif n < 1:
        return 0

    C = [[0 for i in range(n + 1)] for j in range(m + 1)]

    f = trace._frame
    distances = np.array([f.distance(r.geom).values for r in path])

    for i in range(1, m + 1):
        for j in range(1, n + 1):

            # dt = road_to_coord_dist(road, coord)
            dt = distances[j - 1][i - 1]

            if dt < distance_epsilon:
                point_similarity = 1 - dt / distance_epsilon
            else:
                point_similarity = 0

            C[i][j] = max(
                (C[i - 1][j - 1] + point_similarity), C[i][j - 1], C[i - 1][j]
            )

    sim_score = C[m][n] / float(min(m, n))

    e = time.time()
    print(f"SCORE: size: {m * n} \t\t time: {round(e - s, 2)} seconds")

    return sim_score


def new_path(
    road_map: MapInterface,
    trace: Trace,
) -> List[Road]:
    """
    Computes a shortest path and returns the path

    Args:
        road_map: the road map to match to
        trace: the trace to match

    Returns:
        the path that most closely matches the trace
    """
    if len(trace.coords) < 1:
        return []

    origin = trace.coords[0]
    destination = trace.coords[-1]

    new_path = road_map.shortest_path(
        origin, destination, weight=PathWeight.TIME
    )

    return new_path


def split_trajectory_segment(
    road_map: MapInterface,
    trajectory_segment: TrajectorySegment,
) -> List[TrajectorySegment]:
    """
    Splits a trajectory segment based on the provided cutting points.

    Merge back any segments that are too short

    Args:
        road_map: the road map to match to
        trajectory_segment: the trajectory segment to split
        distance_epsilon: the distance epsilon

    Returns:
        a list of split segments or the original segment if it can't be split
    """
    trace = trajectory_segment.trace
    cutting_points = trajectory_segment.cutting_points

    def _short_segment(ts: TrajectorySegment):
        if len(ts.trace) < 2 or len(ts.path) < 1:
            return True
        return False

    if len(trace.coords) < 2:
        # segment is too short to split
        return [trajectory_segment]
    elif len(cutting_points) < 1:
        # no points to cut
        return [trajectory_segment]

    new_paths = []
    new_traces = []

    # using type: ignore below because, trace_index can only be a signedinteger or integer
    # mypy wants it to only be an int, but this should never affect code functionality
    # start
    scp = cutting_points[0]
    new_trace = trace[: scp.trace_index]  # type: ignore
    new_paths.append(new_path(road_map, new_trace))
    new_traces.append(new_trace)

    # mids
    for i in range(len(cutting_points) - 1):
        cp = cutting_points[i]
        ncp = cutting_points[i + 1]
        new_trace = trace[cp.trace_index : ncp.trace_index]  # type: ignore
        new_paths.append(new_path(road_map, new_trace))
        new_traces.append(new_trace)

    # end
    ecp = cutting_points[-1]
    new_trace = trace[ecp.trace_index :]  # type: ignore
    new_paths.append(new_path(road_map, new_trace))
    new_traces.append(new_trace)

    if not any(new_paths):
        # can't split
        return [trajectory_segment]
    elif not any(new_traces):
        # can't split
        return [trajectory_segment]
    else:
        segments = [
            TrajectorySegment(t, p) for t, p in zip(new_traces, new_paths)
        ]

    merged_segments = merge(segments, _short_segment)

    return merged_segments


def same_trajectory_scheme(
    scheme1: TrajectoryScheme, scheme2: TrajectoryScheme
) -> bool:
    """
    Compares two trajectory schemes for equality

    Args:
        scheme1: the first trajectory scheme
        scheme2: the second trajectory scheme

    Returns:
        True if the two schemes are equal, False otherwise
    """
    same_paths = all(map(lambda a, b: a.path == b.path, scheme1, scheme2))
    same_traces = all(
        map(lambda a, b: a.trace.coords == b.trace.coords, scheme1, scheme2)
    )

    return same_paths and same_traces


class StationaryIndex(NamedTuple):
    """
    An index of a stationary point in a trajectory

    Attributes:
        trace_index: the index of the trace
        coord_index: the index of the coordinate
    """

    i_index: List[int]  # i based index on the trace
    c_index: List[Any]  # coordinate ids


def find_stationary_points(trace: Trace) -> List[StationaryIndex]:
    """
    Find the positional index of all stationary points in a trace

    Args:
        trace: the trace to find the stationary points in

    Returns:
        a list of stationary indices
    """
    f = trace._frame
    coords = trace.coords
    dist = f.distance(f.shift())
    index_collections = []
    index = set()
    for i in range(1, len(dist)):
        d = dist.iloc[i]  # distance to previous point
        if d < 0.001:
            index.add(i - 1)
            index.add(i)
        else:
            # there is distance between this point and the previous
            if index:
                l_index = sorted(list(index))
                cids = [coords[li].coordinate_id for li in l_index]
                si = StationaryIndex(l_index, cids)
                index_collections.append(si)
                index = set()

    # catch any group of points at the end
    if index:
        l_index = sorted(list(index))
        cids = [coords[li].coordinate_id for li in l_index]
        si = StationaryIndex(l_index, cids)
        index_collections.append(si)

    return index_collections


def drop_stationary_points(
    trace: Trace, stationary_index: List[StationaryIndex]
) -> Trace:
    """
    Drops stationary points from the trace, keeping the first point

    Args:
        trace: the trace to drop the stationary points from
        stationary_index: the stationary indices to drop

    Returns:
        the trace with the stationary points dropped
    """
    for si in stationary_index:
        trace = trace.drop(si.c_index[1:])

    return trace


def add_matches_for_stationary_points(
    matches: MatchResult,
    stationary_index: List[StationaryIndex],
) -> MatchResult:
    """
    Takes a set of matches and adds duplicate match entries for stationary

    Args:
        matches: the matches to add the stationary points to
        stationary_index: the stationary indices to add

    Returns:
        the matches with the stationary points added
    """
    matches = deepcopy(matches)

    for si in stationary_index:
        mi = si.i_index[0]
        m = matches[mi]
        new_matches = [
            m.set_coordinate(
                Coordinate(ci, geom=m.coordinate.geom, crs=m.coordinate.crs)
            )
            for ci in si.c_index[1:]
        ]
        matches[si.i_index[1] : si.i_index[1]] = new_matches

    return matches
