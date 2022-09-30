from unittest import TestCase

from tests import get_test_dir

from mappymatch.constructs.geofence import Geofence
from mappymatch.utils.crs import LATLON_CRS


class TestGeofence(TestCase):
    def test_trace_from_geojson(self):
        file = get_test_dir() / "test_assets" / "downtown_denver.geojson"

        gfence = Geofence.from_geojson(file)

        self.assertEqual(gfence.crs, LATLON_CRS)
