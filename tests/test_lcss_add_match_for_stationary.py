from __future__ import annotations

from copy import deepcopy
from unittest import TestCase

from shapely.geometry import LineString

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road
from mappymatch.matchers.lcss.ops import (
    StationaryIndex,
    add_matches_for_stationary_points,
)


class TestLCSSAddMatchForStationary(TestCase):
    def test_add_matches_no_stationary_points(self):
        """This will test the "null case" which is to say, no stationary points"""
        # Road(id: str|int, geom: LineString, metadata: dict)
        roads = [
            Road("first st", LineString()),
            Road("second st", LineString()),
            Road("main st", LineString()),
            Road("second str", LineString()),
            Road(123, LineString()),
            Road(234, LineString()),
        ]

        lat_longs = [
            (39.655193, -104.919294),
            (39.655494, -104.91943),
            (39.655801, -104.919567),
            (39.656103, -104.919698),
            (39.656406, -104.919831),
            (39.656707, -104.919964),
        ]
        coords = [Coordinate.from_lat_lon(lat, lon) for lat, lon in lat_longs]
        # Match(road, coordinate, distance)
        matches = [Match(r, c, 0.1) for r, c in zip(roads, coords)]

        # ensure that the expected matches are different from the matches that will be passed in
        expected_matches = deepcopy(matches)

        stationary_index: list[StationaryIndex] = []

        resulting_matches = add_matches_for_stationary_points(
            matches, stationary_index
        )

        self.assertListEqual(expected_matches, resulting_matches)

    def test_add_matches_one_stationary_point_at_beginning(self):
        """Test adding a single stationary point at the beginning"""
        roads = [
            Road("first st", LineString()),
            Road("second st", LineString()),
            Road("main st", LineString()),
            Road("second str", LineString()),
            Road(123, LineString()),
            Road(234, LineString()),
        ]

        lat_longs = [
            (39.655193, -104.919294),
            (39.655494, -104.91943),
            (39.655801, -104.919567),
            (39.656103, -104.919698),
            (39.656406, -104.919831),
            (39.656707, -104.919964),
        ]
        coords = [Coordinate.from_lat_lon(lat, lon) for lat, lon in lat_longs]
        # Match(road, coordinate, distance)
        matches = [Match(r, c, 0.1) for r, c in zip(roads, coords)]

        # ensure that the expected matches are different from the matches that will be passed in
        expected_matches = deepcopy(matches)
        # now, add the expected points
        m = expected_matches[0]
        new_m = m.set_coordinate(
            Coordinate("new", m.coordinate.geom, m.coordinate.crs)
        )
        expected_matches.insert(0, new_m)

        # StationaryIndex( i_index: List[int], c_index: List[Any])
        stationary_index = [StationaryIndex([0, 0], [None, "new"])]

        resulting_matches = add_matches_for_stationary_points(
            matches, stationary_index
        )

        self.assertListEqual(expected_matches, resulting_matches)

    def test_add_matches_one_stationary_point_at_end(self):
        """Test adding a single stationary point at the end"""
        # Road(id: str|int, geom: LineString, metadata: dict)
        roads = [
            Road("first st", LineString()),
            Road("second st", LineString()),
            Road("main st", LineString()),
            Road("second str", LineString()),
            Road(123, LineString()),
            Road(234, LineString()),
        ]

        lat_longs = [
            (39.655193, -104.919294),
            (39.655494, -104.91943),
            (39.655801, -104.919567),
            (39.656103, -104.919698),
            (39.656406, -104.919831),
            (39.656707, -104.919964),
        ]
        coords = [Coordinate.from_lat_lon(lat, lon) for lat, lon in lat_longs]
        # Match(road, coordinate, distance)
        matches = [Match(r, c, 0.1) for r, c in zip(roads, coords)]

        # ensure that the expected matches are different from the matches that will be passed in
        expected_matches = deepcopy(matches)
        # now, add the expected points
        m = expected_matches[-1]
        new_m = m.set_coordinate(
            Coordinate("new", m.coordinate.geom, m.coordinate.crs)
        )
        expected_matches.append(new_m)

        # StationaryIndex( i_index: List[int], c_index: List[Any])
        stationary_index = [StationaryIndex([-1, len(matches)], [None, "new"])]

        resulting_matches = add_matches_for_stationary_points(
            matches, stationary_index
        )

        self.assertListEqual(expected_matches, resulting_matches)

    def test_add_matches_one_stationary_point_in_middle(self):
        """Test adding a single stationary point in the middle"""
        # Road(id: str|int, geom: LineString, metadata: dict)
        roads = [
            Road("first st", LineString()),
            Road("second st", LineString()),
            Road("main st", LineString()),
            Road("second str", LineString()),
            Road(123, LineString()),
            Road(234, LineString()),
        ]

        lat_longs = [
            (39.655193, -104.919294),
            (39.655494, -104.91943),
            (39.655801, -104.919567),
            (39.656103, -104.919698),
            (39.656406, -104.919831),
            (39.656707, -104.919964),
        ]
        coords = [Coordinate.from_lat_lon(lat, lon) for lat, lon in lat_longs]
        # Match(road, coordinate, distance)
        matches = [Match(r, c, 0.1) for r, c in zip(roads, coords)]

        # ensure that the expected matches are different from the matches that will be passed in
        expected_matches = deepcopy(matches)
        # now, add the expected points
        m = expected_matches[-1]
        new_m = m.set_coordinate(
            Coordinate("new", m.coordinate.geom, m.coordinate.crs)
        )
        expected_matches[-1:-1] = [new_m]

        # StationaryIndex( i_index: List[int], c_index: List[Any])
        stationary_index = [StationaryIndex([-1, -1], [None, "new"])]

        resulting_matches = add_matches_for_stationary_points(
            matches, stationary_index
        )

        self.assertListEqual(expected_matches, resulting_matches)

        expected_matches = deepcopy(matches)
        indx = len(matches) // 2
        m = expected_matches[indx]
        new_m = m.set_coordinate(
            Coordinate("new", m.coordinate.geom, m.coordinate.crs)
        )
        expected_matches.insert(indx, new_m)
        stationary_index = [StationaryIndex([indx, indx], [None, "new"])]

        resulting_matches = add_matches_for_stationary_points(
            matches, stationary_index
        )

        self.assertListEqual(expected_matches, resulting_matches)

    def test_add_matches_multiple_stationary_points(self):
        """Test adding multiple stationary points"""
        # Road(id: str|int, geom: LineString, metadata: dict)
        roads = [
            Road("first st", LineString()),
            Road("second st", LineString()),
            Road("main st", LineString()),
            Road("second str", LineString()),
            Road(123, LineString()),
            Road(234, LineString()),
        ]

        lat_longs = [
            (39.655193, -104.919294),
            (39.655494, -104.91943),
            (39.655801, -104.919567),
            (39.656103, -104.919698),
            (39.656406, -104.919831),
            (39.656707, -104.919964),
        ]
        coords = [Coordinate.from_lat_lon(lat, lon) for lat, lon in lat_longs]
        # Match(road, coordinate, distance)
        matches: list[Match] = [
            Match(r, c, 0.1) for r, c in zip(roads, coords)
        ]

        # ensure that the expected matches are different from the matches that will be passed in
        expected_matches = deepcopy(matches)
        # now, add the expected points
        indx = len(matches) // 2
        m = expected_matches[indx]
        coord_ids = ["alpha", "beta", "gamma"]
        new_matches = [
            m.set_coordinate(
                Coordinate(id, m.coordinate.geom, m.coordinate.crs)
            )
            for id in coord_ids
        ]
        expected_matches[indx + 1 : indx + 1] = new_matches

        # StationaryIndex( i_index: List[int], c_index: List[Any])
        stationary_index = [
            StationaryIndex([indx, indx + 1], [None] + coord_ids)
        ]

        resulting_matches = add_matches_for_stationary_points(
            matches, stationary_index
        )

        self.assertListEqual(expected_matches, resulting_matches)
