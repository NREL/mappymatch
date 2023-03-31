from unittest import TestCase

import pandas as pd
from shapely.geometry import LineString

from mappymatch.constructs.road import Road
from mappymatch.constructs.trace import Trace
from mappymatch.matchers.lcss.constructs import TrajectorySegment
from mappymatch.matchers.lcss.utils import forward_merge


class TestLCSSMatcherForwardMerge(TestCase):
    def test_forward_merge_beginning(self):
        """
        This will test that forward_merge can merge items at the beginning of the list
        """
        starting_list = [1, 2, 3, 4, 5]

        def condition(x):
            return x < 3

        expected_list = [6, 4, 5]

        resulting_list = forward_merge(starting_list, condition=condition)

        self.assertListEqual(expected_list, resulting_list)

    def test_forward_merge_ending_no_merge(self):
        """
        This will test that forward_merge can merge items at the end of the list with
        no other merges in the list
        """
        starting_list = [1, 2, 3, 4, 5]

        def condition(x):
            return x > 3

        expected_list = [1, 2, 3, 9]

        resulting_list = forward_merge(starting_list, condition=condition)

        self.assertListEqual(expected_list, resulting_list)

    def test_forward_merge_middle(self):
        """
        This will test that forward_merge can merge items in the middle of the list
        """
        starting_list = [1, 2, 4, 4, 2, 2]

        def condition(x):
            return x > 3

        expected_list = [1, 2, 10, 2]

        resulting_list = forward_merge(starting_list, condition=condition)

        self.assertListEqual(expected_list, resulting_list)

    def test_forward_merge_multi_merges(self):
        """
        This will test that forward_merge works for multiple segments including a
        segment at the end
        """
        starting_list = [1, 2, 3, 6, 4, 2, 3, 1, 6, 7, 3, 4, 3, 3]

        def condition(x):
            return x < 4

        expected_list = [12, 4, 12, 7, 7, 6]

        resulting_list = forward_merge(starting_list, condition=condition)

        self.assertListEqual(expected_list, resulting_list)

    def test_forward_merge_trajectory_segments(self):
        """
        This will test that a list of trajectory segments can merge
        """
        # setup inputted trajectory segments
        trace_1 = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]},
                index=[0],
            )
        )
        trace_2 = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                },
                index=[1, 2],
            )
        )
        trace_3 = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.656103], "longitude": [-104.919698]},
                index=[3],
            )
        )
        trace_4 = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.656406, 39.656707, 39.657005],
                    "longitude": [-104.919831, -104.919964, -104.920099],
                },
                index=[4, 5, 6],
            )
        )
        trace_5 = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.657303, 39.657601],
                    "longitude": [-104.920229, -104.92036],
                },
                index=[7, 8],
            )
        )

        road_1 = [
            Road(
                "first st",
                LineString(),
            )
        ]
        road_2 = [
            Road(
                "second st",
                LineString(),
            )
        ]
        road_3 = [Road(234, LineString())]
        road_4 = [
            Road(
                "first st",
                LineString(),
            ),
            Road(
                "second st",
                LineString(),
            ),
            Road(123, LineString()),
        ]
        road_5 = [
            Road(
                "main st",
                LineString(),
            ),
            Road(
                "second str",
                LineString(),
            ),
        ]

        segment_1 = TrajectorySegment(trace_1, road_1)
        segment_2 = TrajectorySegment(trace_2, road_2)
        segment_3 = TrajectorySegment(trace_3, road_3)
        segment_4 = TrajectorySegment(trace_4, road_4)
        segment_5 = TrajectorySegment(trace_5, road_5)

        starting_list = [segment_1, segment_2, segment_3, segment_4, segment_5]

        # create a condition function for the merge function
        def _merge_condition(ts: TrajectorySegment):
            if len(ts.trace) < 2:
                return True
            return False

        condition = _merge_condition

        # create the expected trajectory segments
        expected_trace_1 = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655193, 39.655494, 39.655801],
                    "longitude": [-104.919294, -104.91943, -104.919567],
                }
            )
        )
        expected_trace_2 = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.656103, 39.656406, 39.656707, 39.657005],
                    "longitude": [
                        -104.919698,
                        -104.919831,
                        -104.919964,
                        -104.920099,
                    ],
                }
            )
        )
        expected_trace_3 = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.657303, 39.657601],
                    "longitude": [-104.920229, -104.92036],
                }
            )
        )

        expected_road_1 = [
            Road(
                "first st",
                LineString(),
            ),
            Road(
                "second st",
                LineString(),
            ),
        ]
        expected_road_2 = [
            Road(234, LineString()),
            Road(
                "first st",
                LineString(),
            ),
            Road(
                "second st",
                LineString(),
            ),
            Road(123, LineString()),
        ]
        expected_road_3 = [
            Road(
                "main st",
                LineString(),
            ),
            Road(
                "second str",
                LineString(),
            ),
        ]

        expected_segment_1 = TrajectorySegment(
            expected_trace_1, expected_road_1
        )
        expected_segment_2 = TrajectorySegment(
            expected_trace_2, expected_road_2
        )
        expected_segment_3 = TrajectorySegment(
            expected_trace_3, expected_road_3
        )

        expected_list = [
            expected_segment_1,
            expected_segment_2,
            expected_segment_3,
        ]

        resulting_list = forward_merge(starting_list, condition=condition)

        # confirm forward merge accuracy
        self.assertEqual(len(expected_list), len(resulting_list))
        for expected_trajectory, resulted_trajectory in zip(
            expected_list, resulting_list
        ):
            # confirm that the coordinates are the same
            self.assertEqual(
                len(expected_trajectory.trace), len(resulted_trajectory.trace)
            )
            for expected_trace, resulted_trace in zip(
                expected_trajectory.trace, resulted_trajectory.trace
            ):
                self.assertEqual(
                    len(expected_trace.coords), len(resulted_trace.coords)
                )
                for expected_coord, resulted_coord in zip(
                    expected_trace.coords, resulted_trace.coords
                ):
                    self.assertEqual(expected_coord.geom, resulted_coord.geom)

            # confirm that the paths are the same
            self.assertListEqual(
                expected_trajectory.path, resulted_trajectory.path
            )
