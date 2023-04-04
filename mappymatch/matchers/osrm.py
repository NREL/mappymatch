from __future__ import annotations

import logging

import requests

from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road, RoadId
from mappymatch.constructs.trace import Trace
from mappymatch.matchers.matcher_interface import MatcherInterface, MatchResult
from mappymatch.utils.crs import LATLON_CRS
from mappymatch.utils.url import multiurljoin

log = logging.getLogger(__name__)

DEFAULT_OSRM_ADDRESS = "http://router.project-osrm.org"


def parse_osrm_json(j: dict, trace: Trace) -> list[Match]:
    """
    parse the json response from the osrm match service

    we're looking for the osm node ids which should be in the form:

    { 'matchings':
        [{ 'legs':
            [{ 'annotations':
                {'nodes': [node_id, node_id] }
            }]
        }]
    }

    :param j: the json object
    :return:
    """
    matchings = j.get("matchings")
    if not matchings:
        raise ValueError("could not find any link matchings in response")

    legs = matchings[0].get("legs")
    if not legs:
        raise ValueError("could not find any link legs in response")

    def _parse_leg(d: dict, i: int) -> Match:
        annotation = d.get("annotation")
        if not annotation:
            raise ValueError("leg has no annotation information")
        nodes = annotation.get("nodes")
        if not nodes:
            raise ValueError("leg has no osm node information")
        origin_junction_id = f"{nodes[0]}"
        destination_junction_id = f"{nodes[0]}"

        # TODO: we need to get geometry, distance info from OSRM if available
        road_id = RoadId(origin_junction_id, destination_junction_id, 0)
        road = Road(
            road_id=road_id,
            geom=None,
        )
        match = Match(
            road=road, coordinate=trace.coords[i], distance=float("infinity")
        )
        return match

    return [_parse_leg(d, i) for i, d in enumerate(legs)]


class OsrmMatcher(MatcherInterface):
    """
    pings an OSRM server for map matching
    """

    def __init__(
        self,
        osrm_address=DEFAULT_OSRM_ADDRESS,
        osrm_profile="driving",
        osrm_version="v1",
    ):
        self.osrm_api_base = multiurljoin(
            [osrm_address, "match", osrm_version, osrm_profile]
        )

    def match_trace(self, trace: Trace) -> MatchResult:
        if not trace.crs == LATLON_CRS:
            raise TypeError(
                f"this matcher requires traces to be in the CRS of EPSG:{LATLON_CRS.to_epsg()} "
                f"but found EPSG:{trace.crs.to_epsg()}"
            )

        if len(trace.coords) > 100:
            trace = trace.downsample(100)

        coordinate_str = ""
        for coord in trace.coords:
            coordinate_str += f"{coord.x},{coord.y};"

        # remove the trailing semicolon
        coordinate_str = coordinate_str[:-1]

        osrm_request = (
            self.osrm_api_base + coordinate_str + "?annotations=true"
        )
        print(osrm_request)

        r = requests.get(osrm_request)

        if not r.status_code == requests.codes.ok:
            r.raise_for_status()

        result = parse_osrm_json(r.json(), trace)

        return MatchResult(result)

    def match_trace_batch(self, trace_batch: list[Trace]) -> list[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
