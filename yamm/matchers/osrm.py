import requests

from yamm.matchers.matcher_interface import *
from yamm.utils.url import multiurljoin

# TODO: find a live osrm instance and substitute this
DEFAULT_OSRM_ADDRESS = "http://router.project-osrm.org"


class OSRM(MatcherInterface):
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
        coordinate_str = ""
        for coord in trace:
            coordinate_str += f"{coord.lon},{coord.lat};"

        # remove the trailing semicolon
        coordinate_str = coordinate_str[:-1]

        osrm_request = self.osrm_api_base + coordinate_str

        r = requests.get(osrm_request)
        # TODO: process osrm response

    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        return [self.match_trace(t) for t in trace_batch]
