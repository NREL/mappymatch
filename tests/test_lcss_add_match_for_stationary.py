from __future__ import annotations
from copy import deepcopy
from unittest import TestCase

from pyproj import CRS
from shapely.geometry import LineString
from shapely.geometry import Point

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road
from mappymatch.matchers.lcss.ops import StationaryIndex
from mappymatch.matchers.lcss.ops import add_matches_for_stationary_points

class TestLCSSAddMatchForStationary(TestCase):
    def test_add_matches_no_stationary_points(self):
        stationary_index: list[StationaryIndex] = []

        # Road(id: str|int, geom: LineString, metadata: dict)
        roads: list[Road] = [
            Road("first st", LineString(), {}),
            Road("second st", LineString(), {}),
            Road("main st", LineString(), {}),
            Road("second str", LineString(), {}),
            Road(123, LineString(), {}),
            Road(234, LineString(), {}),
        ]

        lat_longs = [
            (39.655193,-104.919294),
            (39.655494,-104.91943),
            (39.655801,-104.919567),
            (39.656103,-104.919698),
            (39.656406,-104.919831),
            (39.656707,-104.919964),
        ]
        coords: list[Coordinate] = [Coordinate.from_lat_lon(lat, lon) for lat, lon in lat_longs]

        # Match(road, coordinate, distance)
        matches: list[Match] = [Match(r, c, 0.1) for r, c in zip(roads, coords)]

        expected_matches = deepcopy(matches)

        resulting_matches = add_matches_for_stationary_points(matches, stationary_index)

        self.assertListEqual(expected_matches, resulting_matches)

