from unittest import TestCase

from mappymatch.constructs.trace import Trace
from mappymatch.matchers.valhalla import ValhallaMatcher
from tests import get_test_dir


class TestTrace(TestCase):
    def test_valhalla_on_small_trace(self):
        file = get_test_dir() / "test_assets" / "test_trace.geojson"

        trace = Trace.from_geojson(file, xy=False)

        matcher = ValhallaMatcher()

        result = matcher.match_trace(trace)

        match_df = result.matches_to_dataframe()
        _ = result.path_to_dataframe()

        self.assertEqual(len(match_df), len(trace))
