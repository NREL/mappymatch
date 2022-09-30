from unittest import TestCase

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.utils.crs import LATLON_CRS, XY_CRS


class TestCoordinate(TestCase):
    def test_coordinate_to_same_crs(self):
        c = Coordinate.from_lat_lon(39.755720, -104.994206)

        self.assertEqual(c.crs, LATLON_CRS)

        new_c = c.to_crs(4326)

        self.assertEqual(new_c.crs, LATLON_CRS)

    def test_coordinate_to_new_crs(self):
        c = Coordinate.from_lat_lon(39.755720, -104.994206)

        new_c = c.to_crs(XY_CRS)

        self.assertEqual(new_c.crs, XY_CRS)

    def test_coordinate_to_bad_crs(self):
        c = Coordinate.from_lat_lon(39.755720, -104.994206)

        bad_crs = -1

        self.assertRaises(ValueError, c.to_crs, bad_crs)
