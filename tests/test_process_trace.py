from unittest import TestCase

from mappymatch.constructs.trace import Trace
from mappymatch.utils.process_trace import remove_bad_start_from_trace
from tests import get_test_dir


class TestProcessTrace(TestCase):
    def test_remove_bad_start_from_trace(self):
        """
        a test to ensure that the gap in the beginning of the trace is removed
        """
        tfile = get_test_dir() / "test_assets" / "trace_bad_start.geojson"

        trace = Trace.from_geojson(tfile, xy=True)
        bad_point = trace.coords[0]

        trace = remove_bad_start_from_trace(trace, 30)

        self.assertTrue(
            bad_point not in trace.coords,
            f"trace should have the first point {bad_point} removed",
        )
