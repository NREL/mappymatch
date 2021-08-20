from unittest import TestCase

from tests import test_dir
from yamm.constructs.trace import Trace
from yamm.utils.process_trace import preprocess_trace


class TestProcessTrace(TestCase):

    def test_preprocess_trace(self):
        """
        a test to ensure that the gap in the beginning of the trace is removed
        """
        tfile = test_dir() / "test_assets" / "trace_bad_start.geojson"

        trace = Trace.from_geojson(tfile, xy=True)
        bad_point = trace.coords[0]

        trace = preprocess_trace(trace, 30)

        self.assertTrue(bad_point not in trace.coords, f'trace should have the first point {bad_point} removed')
