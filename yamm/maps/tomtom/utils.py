import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString
from sqlalchemy.future import Engine

from yamm.constructs.geofence import Geofence
from yamm.utils.crs import XY_CRS, LATLON_CRS
from yamm.utils.exceptions import MapException


def get_tomtom_gdf_2021(
    sql_con: Engine, geofence: Geofence, xy: bool = True
) -> gpd.GeoDataFrame:
    """
    Pull TomTom road links and return a geo dataframe

    NOTE: this is designed for TomTom 2021 Multinet

    :param sql_con: the sql connection
    :param geofence: the boundary of the network to pull
    :param xy: whether to return the data in projected xy coordinates

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

    if gdf.empty:
        raise MapException("road network has no links; check geofence boundaries")

    if not gdf.crs:
        gdf.crs = LATLON_CRS

    # add default speed to missing speeds
    gdf["speed_average_neg"] = gdf.speed_average_neg.fillna(20)
    gdf["speed_average_pos"] = gdf.speed_average_pos.fillna(20)
    gdf["kilometers"] = gdf.centimeters * 0.00001
    gdf["neg_minutes"] = (gdf.kilometers / gdf.speed_average_neg) * 60
    gdf["pos_minutes"] = (gdf.kilometers / gdf.speed_average_pos) * 60

    if xy:
        gdf = gdf.to_crs(XY_CRS)

    return gdf


def get_tomtom_gdf_2017(
    sql_con: Engine, geofence: Geofence, xy: bool = True
) -> gpd.GeoDataFrame:
    """
    Pull TomTom road links and return a geo dataframe
    NOTE: this is designed for TomTom 2017 Multinet
    :param sql_con: the sql connection
    :param geofence: the boundary of the network to pull
    :param xy: whether to return the data in projected xy coordinates

    :return: a geo dataframe with the road links
    """
    q = f"""
    select mn.id, f_jnctid, t_jnctid, frc, backrd, rdcond, privaterd, roughrd, 
    meters, minutes, oneway, wkb_geometry 
    from tomtom_multinet_2017.multinet_2017 as mn
    where ST_Within(mn.wkb_geometry, ST_GeomFromEWKT('SRID={geofence.crs.to_epsg()};{geofence.geometry.wkt}'))
    """
    raw_gdf = gpd.GeoDataFrame.from_postgis(
        q,
        con=sql_con,
        geom_col="wkb_geometry",
    )
    if raw_gdf.empty:
        raise MapException("road network has no links; check geofence boundaries")

    if not raw_gdf.crs:
        raw_gdf.crs = LATLON_CRS

    raw_gdf["kilometers"] = raw_gdf.meters / 1000

    raw_gdf = raw_gdf[(raw_gdf.rdcond < 2) & (raw_gdf.frc < 8)].fillna(0)

    if xy:
        raw_gdf = raw_gdf.to_crs(XY_CRS)

    return raw_gdf


def tomtom_gdf_to_nx_graph_2021(gdf: gpd.geodataframe.GeoDataFrame) -> nx.MultiDiGraph:
    """
    Builds a networkx graph from a tomtom geo dataframe

    NOTE: this is designed for TomTom 2021 Multinet

    :param gdf: the tomtom geo dataframe

    :return: a tomtom networkx graph
    """
    oneway_ft = gdf[gdf.simple_traffic_direction == 2]
    oneway_tf = gdf[gdf.simple_traffic_direction == 3]
    twoway = gdf[gdf.simple_traffic_direction.isin([1, 9])]

    twoway_edges_tf = [
        (
            t,
            f,
            nid,
            {
                "kilometers": km,
                "minutes": mn,
                "geom": LineString(reversed(g.coords)),
            },
        )
        for t, f, nid, km, mn, g in zip(
            twoway.junction_id_to.values,
            twoway.junction_id_from.values,
            twoway.netw_id,
            twoway.kilometers.values,
            twoway.neg_minutes.values,
            twoway.geom.values,
        )
    ]

    twoway_edges_ft = [
        (
            f,
            t,
            nid,
            {
                "kilometers": km,
                "minutes": mn,
                "geom": g,
            },
        )
        for t, f, nid, km, mn, g in zip(
            twoway.junction_id_to.values,
            twoway.junction_id_from.values,
            twoway.netw_id,
            twoway.kilometers.values,
            twoway.pos_minutes.values,
            twoway.geom.values,
        )
    ]

    oneway_edges_ft = [
        (
            f,
            t,
            nid,
            {
                "kilometers": km,
                "minutes": mn,
                "geom": g,
            },
        )
        for t, f, nid, km, mn, g in zip(
            oneway_ft.junction_id_to.values,
            oneway_ft.junction_id_from.values,
            oneway_ft.netw_id,
            oneway_ft.kilometers.values,
            oneway_ft.pos_minutes.values,
            oneway_ft.geom.values,
        )
    ]
    oneway_edges_tf = [
        (
            t,
            f,
            nid,
            {
                "kilometers": km,
                "minutes": mn,
                "geom": LineString(reversed(g.coords)),
            },
        )
        for t, f, nid, km, mn, g in zip(
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

    sg_components = nx.strongly_connected_components(G)

    if not sg_components:
        raise MapException(
            "road network has no strongly connected components and is not routable; "
            "check polygon boundaries."
        )

    G = nx.MultiDiGraph(G.subgraph(max(sg_components, key=len)))

    G.graph["crs"] = gdf.crs

    return G


def tomtom_gdf_to_nx_graph_2017(gdf: gpd.geodataframe.GeoDataFrame) -> nx.MultiDiGraph:
    """
    Builds a networkx graph from a tomtom geo dataframe
    NOTE: this is designed for TomTom 2017 Multinet
    :param gdf: the tomtom geo dataframe
    :return: a tomtom networkx graph
    """
    gdf["id"] = gdf.id.astype(int)
    gdf["f_jnctid"] = gdf.f_jnctid.astype(int)
    gdf["t_jnctid"] = gdf.t_jnctid.astype(int)
    gdf["f_lon"] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[0][0])
    gdf["f_lat"] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[0][1])
    gdf["t_lon"] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[-1][0])
    gdf["t_lat"] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[-1][1])
    oneway_ft = gdf[gdf.oneway == "FT"]
    oneway_tf = gdf[gdf.oneway == "TF"]
    twoway = gdf[~(gdf.oneway == "FT") & ~(gdf.oneway == "TF")]

    twoway_edges_tf = [
        (
            t,
            f,
            -k,
            {
                "kilometers": mt,
                "minutes": mn,
                "geom": LineString(reversed(g.coords)),
            },
        )
        for t, f, k, mt, mn, g in zip(
            twoway.t_jnctid.values,
            twoway.f_jnctid.values,
            twoway.id,
            twoway.kilometers.values,
            twoway.minutes.values,
            twoway.wkb_geometry.values,
        )
    ]
    twoway_edges_ft = [
        (
            f,
            t,
            k,
            {
                "kilometers": mt,
                "minutes": mn,
                "geom": g,
            },
        )
        for t, f, k, mt, mn, g in zip(
            twoway.t_jnctid.values,
            twoway.f_jnctid.values,
            twoway.id,
            twoway.kilometers.values,
            twoway.minutes.values,
            twoway.wkb_geometry.values,
        )
    ]
    oneway_edges_ft = [
        (
            f,
            t,
            k,
            {
                "kilometers": mt,
                "minutes": mn,
                "geom": g,
            },
        )
        for t, f, k, mt, mn, g in zip(
            oneway_ft.t_jnctid.values,
            oneway_ft.f_jnctid.values,
            oneway_ft.id,
            oneway_ft.kilometers.values,
            oneway_ft.minutes.values,
            oneway_ft.wkb_geometry.values,
        )
    ]
    oneway_edges_tf = [
        (
            t,
            f,
            -k,
            {
                "kilometers": mt,
                "minutes": mn,
                "geom": LineString(reversed(g.coords)),
            },
        )
        for t, f, k, mt, mn, g in zip(
            oneway_tf.t_jnctid.values,
            oneway_tf.f_jnctid.values,
            oneway_tf.id,
            oneway_tf.kilometers.values,
            oneway_tf.minutes.values,
            oneway_tf.wkb_geometry.values,
        )
    ]

    G = nx.MultiDiGraph()
    G.add_edges_from(twoway_edges_tf)
    G.add_edges_from(twoway_edges_ft)
    G.add_edges_from(oneway_edges_ft)
    G.add_edges_from(oneway_edges_tf)

    sg_components = nx.strongly_connected_components(G)

    if not sg_components:
        raise MapException(
            "road network has no strongly connected components and is not routable; "
            "check polygon boundaries."
        )

    G = nx.MultiDiGraph(G.subgraph(max(sg_components, key=len)))

    G.graph["crs"] = gdf.crs

    return G
