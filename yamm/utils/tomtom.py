import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString
from sqlalchemy.future import Engine

from yamm.constructs.geofence import Geofence
from yamm.utils.crs import XY_CRS


def get_tomtom_gdf(sql_con: Engine, geofence: Geofence) -> gpd.GeoDataFrame:
    """
    Pull TomTom road links and return a geo dataframe

    NOTE: this is designed for TomTom 2021 Multinet

    :param sql_con: the sql connection
    :param geofence: the boundary of the network to pull

    :return: a geo dataframe with the road links
    """
    q = f"""
        select * 
        from tomtom_2021.network as mn
        where ST_Within(mn.geom, ST_GeomFromEWKT('SRID={geofence.crs.to_epsg()};{geofence.geometry.wkt}'))
        """
    gdf = gpd.GeoDataFrame.from_postgis(
        q,
        con=sql_con,
        geom_col="geom",
    )

    # add default speed to missing speeds
    gdf['speed_average_neg'] = gdf.speed_average_neg.fillna(20)
    gdf['speed_average_pos'] = gdf.speed_average_pos.fillna(20)
    gdf['kilometers'] = gdf.centimeters * 0.00001
    gdf['neg_minutes'] = (gdf.kilometers / gdf.speed_average_neg) * 60
    gdf['pos_minutes'] = (gdf.kilometers / gdf.speed_average_pos) * 60

    return gdf


def tomtom_gdf_to_nx_graph(gdf: gpd.geodataframe.GeoDataFrame) -> nx.MultiDiGraph:
    """
    Builds a networkx graph from a tomtom geo dataframe

    NOTE: this is designed for TomTom 2021 Multinet

    :param gdf: the tomtom geo dataframe

    :return: a tomtom networkx graph
    """
    gdf = gdf.to_crs(XY_CRS)

    # add default speed to missing speeds
    gdf['speed_average_neg'] = gdf.speed_average_neg.fillna(20)
    gdf['speed_average_pos'] = gdf.speed_average_pos.fillna(20)
    gdf['kilometers'] = gdf.centimeters * 0.00001
    gdf['neg_minutes'] = (gdf.kilometers / gdf.speed_average_neg) * 60
    gdf['pos_minutes'] = (gdf.kilometers / gdf.speed_average_pos) * 60

    oneway_ft = gdf[gdf.simple_traffic_direction == 2]
    oneway_tf = gdf[gdf.simple_traffic_direction == 3]
    twoway = gdf[gdf.simple_traffic_direction.isin([1, 9])]

    twoway_edges_tf = [
        (t, f, nid, {
            'kilometers': km,
            'minutes': mn,
            'geom': LineString(reversed(g.coords)),
        }) for t, f, nid, km, mn, g in zip(
            twoway.junction_id_to.values,
            twoway.junction_id_from.values,
            twoway.netw_id,
            twoway.kilometers.values,
            twoway.neg_minutes.values,
            twoway.geom.values,
        )
    ]

    twoway_edges_ft = [
        (f, t, nid, {
            'kilometers': km,
            'minutes': mn,
            'geom': g,
        }) for t, f, nid, km, mn, g in zip(
            twoway.junction_id_to.values,
            twoway.junction_id_from.values,
            twoway.netw_id,
            twoway.kilometers.values,
            twoway.pos_minutes.values,
            twoway.geom.values,
        )
    ]

    oneway_edges_ft = [
        (f, t, nid, {
            'kilometers': km,
            'minutes': mn,
            'geom': g,
        }) for t, f, nid, km, mn, g in zip(
            oneway_ft.junction_id_to.values,
            oneway_ft.junction_id_from.values,
            oneway_ft.netw_id,
            oneway_ft.kilometers.values,
            oneway_ft.pos_minutes.values,
            oneway_ft.geom.values,
        )
    ]
    oneway_edges_tf = [
        (t, f, nid, {
            'kilometers': km,
            'minutes': mn,
            'geom': LineString(reversed(g.coords)),
        }) for t, f, nid, km, mn, g in zip(
            oneway_tf.junction_id_to.values,
            oneway_tf.junction_id_from.values,
            oneway_tf.netw_id,
            oneway_tf.kilometers.values,
            oneway_tf.neg_minutes.values,
            oneway_tf.geom.values,
        )
    ]

    G = nx.MultiDiGraph()
    G.add_edges_from(twoway_edges_tf)
    G.add_edges_from(twoway_edges_ft)
    G.add_edges_from(oneway_edges_ft)
    G.add_edges_from(oneway_edges_tf)

    G = nx.MultiDiGraph(G.subgraph(max(nx.strongly_connected_components(G), key=len)))

    return G
