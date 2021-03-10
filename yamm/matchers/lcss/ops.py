import numpy as np

from yamm.constructs.match import Match
from yamm.constructs.trace import Trace
from yamm.maps.networkx_map import Path
from yamm.matchers.lcss.constructs import TrajectorySegment, CuttingPoint
from yamm.utils.geo import road_to_coord_dist, coord_to_coord_dist


def score(trace: Trace, path: Path, distance_epsilon=10) -> float:
    """
    computes the similarity score between a trace and a path

    :param trace:
    :param path:
    :param distance_epsilon:

    :return:
    """
    m = len(trace)
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
                point_similarity = 1 - (dt / distance_epsilon)
            else:
                point_similarity = 0

            C[i][j] = max((C[i - 1][j - 1] + point_similarity), C[i][j - 1], C[i - 1][j])

    sim_score = C[m][n] / float(min(m, n))

    return sim_score


def score_and_match(trajectory_segment: TrajectorySegment, distance_epsilon=10) -> TrajectorySegment:
    """
    computes the score of a trace, pair matching and also matches the coordinates to the nearest road.

    :param trajectory_segment:
    :param distance_epsilon:

    :return:
    """
    trace = trajectory_segment.trace
    path = trajectory_segment.path

    m = len(trace)
    n = len(path)

    matched_roads = []

    if m < 10:
        # todo: find a better way to handle this edge case
        raise Exception(f"traces of less than 10 points can't be matched")
    elif n < 2:
        # this likely means the trace starts and ends at the same point;
        return trajectory_segment.set_score(0)

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

        matched_roads.append(Match(nearest_road.road_id, min_dist))

    sim_score = C[m][n] / float(min(m, n))

    return trajectory_segment.set_score(sim_score).set_matches(matched_roads)


def compute_cutting_points(trajectory_segment, distance_epsilon=100):
    cutting_thresh = 10

    cutting_points = []

    if not trajectory_segment.matches:
        # no matches computed, let's just split the trajectory based on the furthest points
        start = trajectory_segment.trace.coords[0]
        end = trajectory_segment.trace.coords[-1]
        p1 = np.argmax([coord_to_coord_dist(start, c) for c in trajectory_segment.trace.coords])
        p2 = np.argmax([coord_to_coord_dist(end, c) for c in trajectory_segment.trace.coords])

        cp1 = CuttingPoint(p1, trajectory_segment.trace.coords[p1])
        cp2 = CuttingPoint(p2, trajectory_segment.trace.coords[p2])
        return trajectory_segment.set_cutting_points([cp1, cp2])

    # find furthest point
    i = np.argmax([m.distance for m in trajectory_segment.matches])
    cutting_points.append(CuttingPoint(i, trajectory_segment.trace.coords[i]))

    # collect points that are close to the distance threshold
    for i, m in enumerate(trajectory_segment.matches):
        if abs(m.distance - distance_epsilon) < cutting_thresh:
            cutting_points.append(CuttingPoint(i, trajectory_segment.trace.coords[i]))

    sorted_cuts = sorted(cutting_points, key=lambda c: c.trace_index)
    compressed_cuts = list(compress(sorted_cuts))

    return trajectory_segment.set_cutting_points(compressed_cuts)