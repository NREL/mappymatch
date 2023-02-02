from __future__ import annotations

import json
import logging
from typing import List, Tuple

import numpy as np
import polyline
import requests
from shapely.geometry import LineString

from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road
from mappymatch.constructs.trace import Trace
from mappymatch.matchers.matcher_interface import MatcherInterface, MatchResult
from mappymatch.utils.crs import LATLON_CRS

log = logging.getLogger(__name__)

DEMO_VALHALLA_ADDRESS = "https://valhalla1.openstreetmap.de/trace_attributes"
REQUIRED_ATTRIBUTES = set(
    [
        "edge.way_id",
        "matched.distance_from_trace_point",
        "shape",
        "edge.begin_shape_index",
        "edge.end_shape_index",
        "matched.edge_index",
    ]
)
DEFAULT_ATTRIBUTES = set(
    [
        "edge.length",
        "edge.speed",
    ]
)


def build_path_from_result(
    edges: List[dict], shape: List[Tuple[float, float]]
) -> List[Road]:
    """
    builds a mappymatch path from the result of a Valhalla map matching request
    """
    path = []
    for edge in edges:
        way_id = edge["way_id"]
        start_point_i = edge["begin_shape_index"]
        end_point_i = edge["end_shape_index"]
        start_point = shape[start_point_i]
        end_point = shape[end_point_i]
        geom = LineString([start_point, end_point])

        speed = edge["speed"]
        length = edge["length"]

        metadata = {
            "speed_mph": speed,
            "length_miles": length,
        }

        road = Road(road_id=way_id, geom=geom, metadata=metadata)

        path.append(road)

    return path


def build_match_result(
    trace: Trace, matched_points: List[dict], path: List[Road]
) -> MatchResult:
    """
    builds a mappymatch MatchResult from the result of a Valhalla map matching request
    """
    matches = []
    for i, coord in enumerate(trace.coords):
        mp = matched_points[i]
        ei = mp.get("edge_index")
        dist = mp.get("distance_from_trace_point")
        if ei is None:
            road = None
        else:
            try:
                road = path[ei]
            except IndexError:
                road = None

        if dist is None:
            dist = np.inf

        match = Match(road, coord, dist)

        matches.append(match)

    return MatchResult(matches=matches, path=path)


class ValhallaMatcher(MatcherInterface):
    """
    pings a Valhalla server for map matching
    """

    def __init__(
        self,
        valhalla_url=DEMO_VALHALLA_ADDRESS,
        cost_model="auto",
        shape_match="map_snap",
        attributes=DEFAULT_ATTRIBUTES,
    ):
        self.url_base = valhalla_url
        self.cost_model = cost_model
        self.shape_match = shape_match

        all_attributes = list(REQUIRED_ATTRIBUTES.union(set(attributes)))
        self.attributes = all_attributes

    def match_trace(self, trace: Trace) -> MatchResult:
        if not trace.crs == LATLON_CRS:
            trace = trace.to_crs(LATLON_CRS)

        points = [{"lat": c.y, "lon": c.x} for c in trace.coords]

        json_payload = json.dumps(
            {
                "shape": points,
                "costing": self.cost_model,
                "shape_match": self.shape_match,
                "filters": {
                    "attributes": self.attributes,
                    "action": "include",
                },
                "units": "miles",
            }
        )

        valhalla_request = f"{self.url_base}?json={json_payload}"

        r = requests.get(valhalla_request)

        if not r.status_code == requests.codes.ok:
            r.raise_for_status()

        j = r.json()

        edges = j["edges"]
        shape = polyline.decode(j["shape"], precision=6, geojson=True)
        matched_points = j["matched_points"]

        path = build_path_from_result(edges, shape)
        result = build_match_result(trace, matched_points, path)

        return result

    def match_trace_batch(self, trace_batch: list[Trace]) -> list[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
