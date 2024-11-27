from unittest import TestCase

from mappymatch.constructs.trace import Trace
from mappymatch.utils.process_trace import (
    remove_bad_start_from_trace,
    split_large_trace,
)
from tests import get_test_dir


class TestProcessTrace(TestCase):
    def setUp(self) -> None:
        bad_trace_file = get_test_dir() / "test_assets" / "trace_bad_start.geojson"

        self.trace_bad_start = Trace.from_geojson(bad_trace_file, xy=True)

        trace_file = get_test_dir() / "test_assets" / "test_trace.geojson"

        # This trace has 16 points
        self.trace = Trace.from_geojson(trace_file, xy=True)

    def test_remove_bad_start_from_trace(self):
        """
        a test to ensure that the gap in the beginning of the trace is removed
        """
        bad_point = self.trace_bad_start.coords[0]

        new_trace = remove_bad_start_from_trace(self.trace_bad_start, 30)

        self.assertTrue(
            bad_point not in new_trace.coords,
            f"trace should have the first point {bad_point} removed",
        )

    def test_trace_smaller_than_ideal_size(self):
        result = split_large_trace(self.trace, 20)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.trace)

    def test_trace_equal_to_ideal_size(self):
        result = split_large_trace(self.trace, 16)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.trace)

    def test_ideal_size_zero(self):
        with self.assertRaises(ValueError):
            split_large_trace(self.trace, 0)

    def test_ideal_size(self):
        result = split_large_trace(self.trace, 10)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 16)

    def test_trace_larger_with_merging(self):
        result = split_large_trace(self.trace, 12)  # Splitting into chunks of 12
        self.assertEqual(len(result), 1)  # Expect merging to create a single chunk
        self.assertEqual(len(result[0]), 16)  # All points are in one merged trace
