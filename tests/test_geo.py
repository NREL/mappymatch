from unittest import TestCase

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.utils.geo import coord_to_coord_dist, latlon_to_xy, xy_to_latlon


class TestGeoUtils(TestCase):
    def setUp(self):
        self.lat, self.lon = 40.7128, -74.0060
        self.x, self.y = -8238310.23, 4970071.58

        # We'll use simple x, y coordinates for testing
        self.coordinate_a = Coordinate.from_lat_lon(1, 1)
        self.coordinate_b = Coordinate.from_lat_lon(2, 2)

    def test_xy_to_latlon(self):
        lat, lon = xy_to_latlon(self.x, self.y)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

        self.assertAlmostEqual(lat, self.lat, delta=0.01)
        self.assertAlmostEqual(lon, self.lon, delta=0.01)

    def test_latlon_to_xy(self):
        x, y = latlon_to_xy(self.lat, self.lon)
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)

        self.assertAlmostEqual(x, self.x, delta=0.01)
        self.assertAlmostEqual(y, self.y, delta=0.01)

    def test_xy_to_latlon_and_back(self):
        # Test round-trip conversion
        lat, lon = xy_to_latlon(self.x, self.y)
        x_new, y_new = latlon_to_xy(lat, lon)

        # Ensure the round-trip results are consistent
        self.assertAlmostEqual(self.x, x_new, delta=0.01)
        self.assertAlmostEqual(self.y, y_new, delta=0.01)

    def test_coord_to_coord_dist(self):
        dist = coord_to_coord_dist(self.coordinate_a, self.coordinate_b)
        self.assertIsInstance(dist, float)

        self.assertGreater(dist, 0)
        self.assertAlmostEqual(dist, 1.41, delta=0.01)
