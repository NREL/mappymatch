import logging
from typing import List

from yamm.constructs.road import Road
from yamm.constructs.trace import Trace
from yamm.maps.map_interface import MapInterface
from yamm.matchers.lcss.constructs import TrajectorySegment, TrajectoryScheme
from yamm.matchers.lcss.utils import merge
from yamm.utils.geo import road_to_coord_dist

log = logging.getLogger(__name__)


def score(trace: Trace, path: List[Road], distance_epsilon: float) -> float:
    """
    computes the similarity score between a trace and a path

    :param trace:
    :param path:
    :param distance_epsilon:

    :return:
    """
    m = len(trace.coords)
    n = len(path)

    if m < 2:
        return 0
    elif n < 1:
        return 0

    C = [[0 for i in range(n + 1)] for j in range(m + 1)]

    for i in range(1, m + 1):
        coord = trace.coords[i - 1]
        for j in range(1, n + 1):
            road = path[j - 1]

            dt = road_to_coord_dist(road, coord)

            if dt < distance_epsilon:
                point_similarity = 1 - dt / distance_epsilon
            else:
                point_similarity = 0

            C[i][j] = max((C[i - 1][j - 1] + point_similarity), C[i][j - 1], C[i - 1][j])

    sim_score = C[m][n] / float(min(m, n))

    return sim_score


def new_path(
        road_map: MapInterface,
        trace: Trace,
        distance_epsilon: float,
) -> List[Road]:
    """
    Computes a shortest time and shortest distance path and returns the path that
    most closely matches the trace.

    :param road_map:
    :param trace:
    :param distance_epsilon:

    :return:
    """
    if len(trace.coords) < 1:
        return []

    origin = trace.coords[0]
    destination = trace.coords[-1]

    # todo: make the weight parameter specific to the road map
    time_path = road_map.shortest_path(origin, destination, weight="minutes")
    dist_path = road_map.shortest_path(origin, destination, weight="meters")

    time_score = score(trace, time_path, distance_epsilon)
    dist_score = score(trace, dist_path, distance_epsilon)

    if dist_score > time_score:
        return dist_path
    else:
        return time_path


def split_trajectory_segment(
        road_map: MapInterface,
        trajectory_segment: TrajectorySegment,
        distance_epsilon: float,
) -> List[TrajectorySegment]:
    """
    Splits a trajectory segment based on the provided cutting points.

    Merge back any segments that are too short

    :param road_map: the road map to match to
    :param trajectory_segment: the trajectory segment to split
    :param distance_epsilon: the distance epsilon

    :return: a list of split segments or the original segment if it can't be split
    """
    trace = trajectory_segment.trace
    cutting_points = trajectory_segment.cutting_points

    def _short_segment(ts: TrajectorySegment):
        if len(ts.trace) < 10 or len(ts.path) < 5:
            return True
        return False

    if len(trace.coords) < 10:
        # segment is too short to split
        return [trajectory_segment]
    elif len(cutting_points) < 1:
        # no points to cut
        return [trajectory_segment]

    o = trace.coords[0]
    d = trace.coords[-1]

    new_paths = []
    new_traces = []

    # start
    scp = cutting_points[0]
    new_trace = trace[:scp.trace_index]
    new_paths.append(new_path(road_map, new_trace, distance_epsilon))
    new_traces.append(new_trace)

    # mids
    for i in range(len(cutting_points) - 1):
        cp = cutting_points[i]
        ncp = cutting_points[i + 1]
        new_trace = trace[cp.trace_index:ncp.trace_index]
        new_paths.append(new_path(road_map, new_trace, distance_epsilon))
        new_traces.append(new_trace)

    # end
    ecp = cutting_points[-1]
    new_trace = trace[ecp.trace_index:]
    new_paths.append(new_path(road_map, new_trace, distance_epsilon))
    new_traces.append(new_trace)

    if not any(new_paths):
        # can't split
        return [trajectory_segment]
    elif not any(new_traces):
        # can't split
        return [trajectory_segment]
    else:
        segments = [TrajectorySegment(t, p) for t, p in zip(new_traces, new_paths)]

    merged_segments = merge(segments, _short_segment)

    return merged_segments


def same_trajectory_scheme(
        scheme1: TrajectoryScheme,
        scheme2: TrajectoryScheme) -> bool:
    """
    compares two trajectory schemes for equality

    :param scheme1:
    :param scheme2:

    :return: are the schemes the same?
    """
    same_paths = all(map(lambda a, b: a.path == b.path, scheme1, scheme2))
    same_traces = all(map(lambda a, b: a.trace.coords == b.trace.coords, scheme1, scheme2))

    return same_paths and same_traces
