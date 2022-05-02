from unittest import TestCase, skip

from tests import get_test_dir
from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.maps.nx.readers.osm_readers import read_osm_nxmap
from yamm.utils.crs import XY_CRS, LATLON_CRS


class TestOSMap(TestCase):

    def test_osm_networkx_graph(self):
        gfile = get_test_dir() / "test_assets" / "downtown_denver.geojson"

        geofence = Geofence.from_geojson(gfile)

        osm_map = read_osm_nxmap(geofence)

        # Make sure we can find 31st St near Mestizo-Curtis Park
        mestizo_curtis_park = Coordinate.from_lat_lon(39.761613, -104.977189)
        st31 = osm_map.nearest_road(mestizo_curtis_park.to_crs(XY_CRS))
        # DEBUG: plot the street it choose using geojson.io
        #import geopandas
        #print(geopandas.GeoSeries(st31.geom).set_crs(XY_CRS).to_crs(LATLON_CRS).to_json())
        self.assertEqual(st31.road_id, '1321042414-3323569423')

        # Make sure the graph contains this road segment
        e23_ave_node1 = osm_map.g.nodes[1321042414]
        e23_ave_node2 = osm_map.g.nodes[3323569423]
        self.assertAlmostEqual(e23_ave_node1['lat'], 39.761877, 5)
        self.assertAlmostEqual(e23_ave_node1['lon'], -104.9775733, 5)
        self.assertAlmostEqual(e23_ave_node2['lat'], 39.7602886, 5)
        self.assertAlmostEqual(e23_ave_node2['lon'], -104.9779113, 5)
        self.assertAlmostEqual(osm_map.g.get_edge_data(1321042414, 3323569423, 0)['kilometers'], 0.246787, 5)
