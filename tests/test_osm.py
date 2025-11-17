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
        # This is just a raw osmnx graph pull using the script:
        # tests/test_assets/pull_osm_map.py
        gfile = get_test_dir() / "test_assets" / "osmnx_drive_graph.graphml"

        osmnx_graph = ox.load_graphml(gfile)

        cleaned_graph = parse_osmnx_graph(osmnx_graph, NetworkType.DRIVE)

        self.assertEqual(cleaned_graph.graph["network_type"], NetworkType.DRIVE.value)

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

        # check to make sure we don't have any extra data stored in the edges
        expected_edge_keys = ["geometry", "travel_time", "kilometers", "metadata"]
        expected_node_keys = []

        edges_have_right_keys = all(
            [
                set(d.keys()) == set(expected_edge_keys)
                for _, _, d in cleaned_graph.edges(data=True)
            ]
        )

        self.assertTrue(edges_have_right_keys, "Edges have unexpected keys")

        nodes_have_right_keys = all(
            [
                set(d.keys()) == set(expected_node_keys)
                for _, d in cleaned_graph.nodes(data=True)
            ]
        )

        print(list(cleaned_graph.nodes(data=True))[:5])

        self.assertTrue(nodes_have_right_keys, "Nodes have unexpected keys")
