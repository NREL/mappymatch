from unittest import TestCase

from tests import test_dir
from yamm.constructs.geofence import Geofence
from yamm.maps.osm.utils import get_osm_networkx_graph


class TestOSMap(TestCase):
    def test_osm_networkx_graph(self):
        gfile = test_dir() / "test_assets" / "downtown_denver.geojson"

        geofence = Geofence.from_geojson(gfile)

        nx_graph = get_osm_networkx_graph(geofence)

        edges = nx_graph.edges(data=True)
        nodes = nx_graph.nodes(data=True)
