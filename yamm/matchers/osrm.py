import logging

import requests

from yamm.matchers.matcher_interface import *
from yamm.utils.url import multiurljoin

log = logging.getLogger(__name__)

DEFAULT_OSRM_ADDRESS = "http://router.project-osrm.org"


def parse_osrm_json(j: dict) -> List[LinkId]:
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

    def _parse_leg(d: dict) -> LinkId:
        annotation = d.get("annotation")
        if not annotation:
            raise ValueError("leg has no annotation information")
        nodes = annotation.get('nodes')
        if not nodes:
            raise ValueError('leg has no osm node information')
        link_id = f"({nodes[0]},{nodes[1]})"
        return link_id

    return [_parse_leg(d) for d in legs]


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
        self.osrm_api_base = multiurljoin([osrm_address, "match", osrm_version, osrm_profile])

    def match_trace(self, trace: Trace) -> MatchResult:
        if len(trace) > 100:
            trace = trace.downsample(100)

        coordinate_str = ""
        for coord in trace.coords:
            coordinate_str += f"{coord.lon},{coord.lat};"

        # remove the trailing semicolon
        coordinate_str = coordinate_str[:-1]

        osrm_request = self.osrm_api_base + coordinate_str + "?annotations=true"

        r = requests.get(osrm_request)

        if not r.status_code == requests.codes.ok:
            r.raise_for_status()

        result = parse_osrm_json(r.json())

        return result

    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
