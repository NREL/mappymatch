from unittest import TestCase

import pandas as pd

from mappymatch import package_root
from mappymatch.constructs.trace import Trace
from mappymatch.utils.crs import XY_CRS
from mappymatch.utils.geo import xy_to_latlon
from tests import get_test_dir


class TestTrace(TestCase):
    def test_trace_from_file(self):
        file = package_root() / "resources" / "traces" / "sample_trace_1.csv"

        trace = Trace.from_csv(file)

        self.assertEqual(trace.crs, XY_CRS)
        self.assertEqual(len(trace), 1053)

    def test_trace_from_dataframe(self):
        file = package_root() / "resources" / "traces" / "sample_trace_1.csv"

        df = pd.read_csv(file)

        trace = Trace.from_dataframe(df)

        self.assertEqual(trace.crs, XY_CRS)
        self.assertEqual(len(trace), 1053)

    def test_trace_from_gpx(self):
        file = get_test_dir() / "test_assets" / "test_trace.gpx"
        trace = Trace.from_gpx(file)

        self.assertEqual(trace.crs, XY_CRS)
        self.assertEqual(len(trace), 778)

        # check if the first / last point matches the gpx file
        # in wgs84 lat lon
        pt1 = xy_to_latlon(trace.coords[0].x, trace.coords[0].y)
        pt2 = xy_to_latlon(trace.coords[-1].x, trace.coords[-1].y)
        target_pt1, target_pt2 = (
            (39.74445, -104.97347),
            (
                39.74392,
                -104.9734299,
            ),
        )
        self.assertAlmostEqual(pt1[0], target_pt1[0])
        self.assertAlmostEqual(pt1[1], target_pt1[1])
        self.assertAlmostEqual(pt2[0], target_pt2[0])
        self.assertAlmostEqual(pt2[1], target_pt2[1])
