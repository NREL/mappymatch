# %%
import osmnx as ox

from mappymatch.constructs.geofence import Geofence

# %%
geofence = Geofence.from_geojson("downtown_denver.geojson")
g = ox.graph_from_polygon(
    geofence.geometry,
    network_type="drive",
)

ox.save_graphml(g, "osmnx_drive_graph.graphml")
# %%
