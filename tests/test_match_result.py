from unittest import TestCase

import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.road import Road
from mappymatch.matchers.match_result import Match, MatchResult
from mappymatch.utils.crs import LATLON_CRS

dummy_coordinate_1 = Coordinate("1", Point(1, 1), LATLON_CRS)
dummy_coordinate_2 = Coordinate("2", Point(1, 1), LATLON_CRS)
dummy_line = LineString([(1, 1), (2, 2)])
dummy_road = Road(
    "r",
    geom=dummy_line,
    origin_junction_id=1,
    dest_junction_id=2,
    metadata={"a": 1, "b": 2},
)
dummy_matches = [
    Match(None, dummy_coordinate_1, np.inf),
    Match(dummy_road, dummy_coordinate_2, 1.0),
]
dummy_path = [dummy_road, dummy_road]
dummy_match_result = MatchResult(dummy_matches, dummy_path)


class TestMatchResult(TestCase):
    def test_matches_to_dataframe(self):
        df = dummy_match_result.matches_to_dataframe()
        self.assertTrue(pd.isna(df.iloc[0].road_id))
        self.assertTrue(pd.isna(df.iloc[0].a))
        self.assertTrue(df.iloc[1].road_id == "r")
        self.assertTrue(df.iloc[1].a == 1)
