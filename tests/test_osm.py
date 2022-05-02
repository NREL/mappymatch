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

        # Make sure the graph contains this road segment
        e23_ave_node1 = osm_map.g.nodes[176101784]
        e23_ave_node2 = osm_map.g.nodes[176102601]
        self.assertAlmostEqual(e23_ave_node1['lat'], 39.7578861, 5)
        self.assertAlmostEqual(e23_ave_node1['lon'], -104.9844841, 5)
        self.assertAlmostEqual(e23_ave_node2['lat'], 39.7585533, 5)
        self.assertAlmostEqual(e23_ave_node2['lon'], -104.9853503, 5)
        self.assertAlmostEqual(osm_map.g.get_edge_data(176101784, 176102601, 0)['kilometers'], 0.104817, 5)
