from unittest import TestCase

import networkx as nx
import osmnx as ox

from mappymatch.maps.nx.readers.osm_readers import (
    NetworkType,
    parse_osmnx_graph,
)
from tests import get_test_dir


class TestOSMap(TestCase):
    def test_osm_networkx_graph_drive(self):
        gfile = get_test_dir() / "test_assets" / "osmnx_drive_graph.graphml"

        osmnx_graph = ox.load_graphml(gfile)

        cleaned_graph = parse_osmnx_graph(osmnx_graph, NetworkType.DRIVE)

        self.assertEqual(
            cleaned_graph.graph["network_type"], NetworkType.DRIVE.value
        )

        self.assertTrue(
            nx.is_strongly_connected(cleaned_graph),
            "Graph is not strongly connected",
        )

        has_geom = all(
            [
                d.get("geometry") is not None
                for _, _, d in cleaned_graph.edges(data=True)
            ]
        )
        self.assertTrue(has_geom, "All edges should have geometry")

        # Make sure the graph contains this road segment
        # TODO: this might be a bit unstable since OSM node ids might change
        e23_ave_node1 = cleaned_graph.nodes[1321042414]
        e23_ave_node2 = cleaned_graph.nodes[3323569423]
        self.assertAlmostEqual(e23_ave_node1["lat"], 39.761877, 5)
        self.assertAlmostEqual(e23_ave_node1["lon"], -104.9775733, 5)
        self.assertAlmostEqual(e23_ave_node2["lat"], 39.7602886, 5)
        self.assertAlmostEqual(e23_ave_node2["lon"], -104.9779113, 5)
        self.assertAlmostEqual(
            cleaned_graph.get_edge_data(1321042414, 3323569423, 0)[
                "kilometers"
            ],
            0.246787,
            5,
        )
