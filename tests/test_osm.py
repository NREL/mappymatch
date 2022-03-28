from unittest import TestCase, skip

from tests import get_test_dir
from yamm.constructs.geofence import Geofence
from yamm.maps.nx.readers.osm_readers import read_osm_nxmap


class TestOSMap(TestCase):
    @skip
    def test_osm_networkx_graph(self):
        gfile = get_test_dir() / "test_assets" / "downtown_denver.geojson"

        geofence = Geofence.from_geojson(gfile)

        osm_map = read_osm_nxmap(geofence)
