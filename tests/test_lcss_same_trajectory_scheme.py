from unittest import TestCase

import pandas as pd
from shapely.geometry import LineString

from mappymatch.constructs.road import Road, RoadId
from mappymatch.constructs.trace import Trace
from mappymatch.matchers.lcss.constructs import TrajectorySegment
from mappymatch.matchers.lcss.ops import same_trajectory_scheme


class TestLCSSMatcherSameTrajectoryScheme(TestCase):
    def test_same_trajectory_scheme_equal(self):
        """
        This will test that two equal trajectory schemes are the same
        """
        # setup inputted trajectory segments
        trace_1_a = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_a = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_a = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_a = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_a = TrajectorySegment(trace_1_a, road_1_a)
        segment_2_a = TrajectorySegment(trace_2_a, road_2_a)

        list_a = [segment_1_a, segment_2_a]

        trace_1_b = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_b = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_b = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_b = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_b = TrajectorySegment(trace_1_b, road_1_b)
        segment_2_b = TrajectorySegment(trace_2_b, road_2_b)

        list_b = [segment_1_b, segment_2_b]

        self.assertTrue(same_trajectory_scheme(list_a, list_b))

    def test_same_trajectory_scheme_not_equal_paths(self):
        """
        This will test that two trajectory schemes with same coords, but different paths will not be the same
        """
        # setup inputted trajectory segments
        trace_1_a = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_a = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_a = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_a = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_a = TrajectorySegment(trace_1_a, road_1_a)
        segment_2_a = TrajectorySegment(trace_2_a, road_2_a)

        list_a = [segment_1_a, segment_2_a]

        trace_1_b = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_b = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_b = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_b = [Road(RoadId(1, 2, "not second st"), LineString())]

        segment_1_b = TrajectorySegment(trace_1_b, road_1_b)
        segment_2_b = TrajectorySegment(trace_2_b, road_2_b)

        list_b = [segment_1_b, segment_2_b]

        self.assertFalse(same_trajectory_scheme(list_a, list_b))

    def test_same_trajectory_scheme_not_equal_coords(self):
        """
        This will test that two trajectory schemes with same paths, but different coords will not be the same
        """
        # setup inputted trajectory segments
        trace_1_a = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_a = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-105.91943, -104.919567],
                }
            )
        )

        road_1_a = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_a = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_a = TrajectorySegment(trace_1_a, road_1_a)
        segment_2_a = TrajectorySegment(trace_2_a, road_2_a)

        list_a = [segment_1_a, segment_2_a]

        trace_1_b = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_b = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_b = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_b = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_b = TrajectorySegment(trace_1_b, road_1_b)
        segment_2_b = TrajectorySegment(trace_2_b, road_2_b)

        list_b = [segment_1_b, segment_2_b]

        self.assertFalse(same_trajectory_scheme(list_a, list_b))

    def test_same_trajectory_scheme_not_equal_coords_nor_paths(self):
        """
        This will test that two trajectory schemes with different coords and paths will not be the same
        """
        # setup inputted trajectory segments
        trace_1_a = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_a = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-105.91943, -104.919567],
                }
            )
        )

        road_1_a = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_a = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_a = TrajectorySegment(trace_1_a, road_1_a)
        segment_2_a = TrajectorySegment(trace_2_a, road_2_a)

        list_a = [segment_1_a, segment_2_a]

        trace_1_b = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_b = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_b = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_b = [Road("not second st", LineString())]

        segment_1_b = TrajectorySegment(trace_1_b, road_1_b)
        segment_2_b = TrajectorySegment(trace_2_b, road_2_b)

        list_b = [segment_1_b, segment_2_b]

        self.assertFalse(same_trajectory_scheme(list_a, list_b))

    def test_same_trajectory_scheme_same_trace_equal(self):
        """
        This will test that a trajectory schemes is equal to itself
        """
        # setup inputted trajectory segments
        trace_1_a = Trace.from_dataframe(
            pd.DataFrame(
                data={"latitude": [39.655193], "longitude": [-104.919294]}
            )
        )
        trace_2_a = Trace.from_dataframe(
            pd.DataFrame(
                data={
                    "latitude": [39.655494, 39.655801],
                    "longitude": [-104.91943, -104.919567],
                }
            )
        )

        road_1_a = [Road(RoadId(1, 2, "first st"), LineString())]
        road_2_a = [Road(RoadId(1, 2, "second st"), LineString())]

        segment_1_a = TrajectorySegment(trace_1_a, road_1_a)
        segment_2_a = TrajectorySegment(trace_2_a, road_2_a)

        list_a = [segment_1_a, segment_2_a]

        self.assertTrue(same_trajectory_scheme(list_a, list_a))
