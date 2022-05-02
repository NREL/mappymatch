from unittest import TestCase, skip

from tests import get_test_dir
from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.maps.nx.readers.osm_readers import read_osm_nxmap
from yamm.utils.crs import XY_CRS


class TestOSMap(TestCase):

    def test_osm_networkx_graph(self):
        gfile = get_test_dir() / "test_assets" / "downtown_denver.geojson"

        geofence = Geofence.from_geojson(gfile)

        osm_map = read_osm_nxmap(geofence)

        # Make sure we can find East 23rd Ave within the Denver Zoo.
        denver_zoo = Coordinate.from_lat_lon(39.751029, -104.956666)
        e23_ave = osm_map.nearest_road(denver_zoo.to_crs(XY_CRS))
        self.assertEqual(e23_ave.road_id, '176101784-176102601')
