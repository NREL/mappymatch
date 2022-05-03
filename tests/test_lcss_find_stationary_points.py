from unittest import TestCase

import pandas as pd

from mappymatch.constructs.trace import Trace
from mappymatch.matchers.lcss.ops import (
    StationaryIndex,
    find_stationary_points,
)


class TestLCSSMatcherFindStationaryPoints(TestCase):
    def test_find_stationary_points_matching_points_beginning(self):
        """
        This will test that find_stationary_point can find the stationary points in
        the beginning of the trace
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655193, 39.655193, 39.655494, 39.655801],
                    "longitude": [
                        -104.919294,
                        -104.919294,
                        -104.91943,
                        -104.919567,
                    ],
                }
            )
        )

        expected_list = [
            StationaryIndex(
                [0, 1],
                [trace.coords[0].coordinate_id, trace.coords[1].coordinate_id],
            )
        ]

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)

    def test_find_stationary_points_matching_points_ending(self):
        """
        This will test that find_stationary_point can find the stationary points in
        the ending of the trace
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655193, 39.655494, 39.655801, 39.655801],
                    "longitude": [
                        -104.919294,
                        -104.91943,
                        -104.919567,
                        -104.919567,
                    ],
                }
            )
        )

        expected_list = [
            StationaryIndex(
                [2, 3],
                [trace.coords[2].coordinate_id, trace.coords[3].coordinate_id],
            )
        ]

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)

    def test_find_stationary_points_matching_points_middle(self):
        """
        This will test that find_stationary_point can find the stationary points in
        the middle of the trace
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655193, 39.655494, 39.655494, 39.655801],
                    "longitude": [
                        -104.919294,
                        -104.91943,
                        -104.91943,
                        -104.919567,
                    ],
                }
            )
        )

        expected_list = [
            StationaryIndex(
                [1, 2],
                [trace.coords[1].coordinate_id, trace.coords[2].coordinate_id],
            )
        ]

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)

    def test_find_stationary_points_matching_points_multiple(self):
        """
        This will test that find_stationary_point can find the multiple sets
        of stationary points
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [
                        39.655193,
                        39.655193,
                        39.655193,
                        39.655494,
                        39.655494,
                        39.655801,
                        39.656103,
                        39.656103,
                    ],
                    "longitude": [
                        -104.919294,
                        -104.919294,
                        -104.919294,
                        -104.91943,
                        -104.91943,
                        -104.919567,
                        -104.919698,
                        -104.919698,
                    ],
                }
            )
        )

        expected_list = [
            StationaryIndex(
                [0, 1, 2],
                [
                    trace.coords[0].coordinate_id,
                    trace.coords[1].coordinate_id,
                    trace.coords[2].coordinate_id,
                ],
            ),
            StationaryIndex(
                [3, 4],
                [trace.coords[3].coordinate_id, trace.coords[4].coordinate_id],
            ),
            StationaryIndex(
                [6, 7],
                [trace.coords[6].coordinate_id, trace.coords[7].coordinate_id],
            ),
        ]

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)

    def test_find_stationary_points_matching_points_slightly_different(self):
        """
        This will test that find_stationary_point can find the stationary points that are
        slightly different, but close enough to be stationary
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [
                        39.655193,
                        39.655193001,
                        39.655494,
                        39.655801,
                    ],
                    "longitude": [
                        -104.919294,
                        -104.919294,
                        -104.91943,
                        -104.919567,
                    ],
                }
            )
        )

        expected_list = [
            StationaryIndex(
                [0, 1],
                [trace.coords[0].coordinate_id, trace.coords[1].coordinate_id],
            )
        ]

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)

    def test_find_stationary_points_mathing_points_just_under_limit(self):
        """
        This will test that find_stationary_point can find the stationary points that
        have a distance difference just under .001, making them close enough to be
        stationary
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [
                        39.655193,
                        39.6551930069,
                        39.655494,
                        39.655801,
                    ],
                    "longitude": [
                        -104.919294,
                        -104.919294,
                        -104.91943,
                        -104.919567,
                    ],
                }
            )
        )

        expected_list = [
            StationaryIndex(
                [0, 1],
                [trace.coords[0].coordinate_id, trace.coords[1].coordinate_id],
            )
        ]

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)

    def test_find_stationary_points_mathing_points_just_over_limit(self):
        """
        This will test that find_stationary_point can find points that have a distance
        difference just over .001, making them far enough to not be stationary
        """
        trace = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [
                        39.655193,
                        39.655193007,
                        39.655494,
                        39.655801,
                    ],
                    "longitude": [
                        -104.919294,
                        -104.919294,
                        -104.91943,
                        -104.919567,
                    ],
                }
            )
        )

        expected_list = []

        resulting_list = find_stationary_points(trace=trace)

        self.assertListEqual(expected_list, resulting_list)
