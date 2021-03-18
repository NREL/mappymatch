import geopandas as gpd
import networkx as nx
from pyproj import Transformer
from shapely.geometry import LineString
from sqlalchemy.future import Engine

from yamm.constructs.geofence import Geofence
from yamm.utils.crs import LATLON_CRS, XY_CRS


def compress_tomtom_nx_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    compress the tomtom_nx_graph by removing certain attributes

    :param graph: the graph to compress

    :return: the compressed graph
    """

    # remove the link geometry to save space
    for _, _, data in graph.edges(data=True):
        if 'geom' in data:
            del (data['geom'])

    return graph


def get_tomtom_gdf(sql_con: Engine, geofence: Geofence) -> gpd.GeoDataFrame:
    """
    Pull TomTom road links and return a geo dataframe

    NOTE: this is designed for TomTom 2017 Multinet

    :param sql_con: the sql connection
    :param geofence: the boundary of the network to pull

    :return: a geo dataframe with the road links
    """
    q = f"""
    select mn.id, f_jnctid, t_jnctid, frc, backrd, rdcond, privaterd, roughrd, 
    meters, minutes, oneway, wkb_geometry 
    from tomtom_multinet_2017.multinet_2017 as mn
    where ST_Contains(ST_GeomFromEWKT('SRID={geofence.crs.to_epsg()};{geofence.geometry.wkt}'), 
    ST_GeomFromEWKB(mn.wkb_geometry))
    """
    raw_gdf = gpd.GeoDataFrame.from_postgis(
        q,
        con=sql_con,
        geom_col="wkb_geometry",
    )

    raw_gdf = raw_gdf[
        (raw_gdf.rdcond == 1) &
        (raw_gdf.frc < 7) &
        (raw_gdf.backrd == 0) &
        (raw_gdf.privaterd == 0) &
        (raw_gdf.roughrd == 0)
        ].fillna(0)

    return raw_gdf


def tomtom_gdf_to_nx_graph(gdf: gpd.geodataframe.GeoDataFrame) -> nx.MultiDiGraph:
    """
    Builds a networkx graph from a tomtom geo dataframe

    NOTE: this is designed for TomTom 2017 Multinet

    :param gdf: the tomtom geo dataframe

    :return: a tomtom networkx graph
    """
    gdf['id'] = gdf.id.astype(int)
    gdf['f_jnctid'] = gdf.f_jnctid.astype(int)
    gdf['t_jnctid'] = gdf.t_jnctid.astype(int)
    gdf['f_lon'] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[0][0])
    gdf['f_lat'] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[0][1])
    gdf['t_lon'] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[-1][0])
    gdf['t_lat'] = gdf.wkb_geometry.apply(lambda g: list(g.coords)[-1][1])
    gdf = gdf.to_crs(XY_CRS)
    oneway_ft = gdf[gdf.oneway == 'FT']
    oneway_tf = gdf[gdf.oneway == 'TF']
    twoway = gdf[~(gdf.oneway == 'FT') & ~(gdf.oneway == 'TF')]

    twoway_edges_tf = [
        (t, f, -k, {
            'meters': mt,
            'minutes': mn,
            'geom': LineString(reversed(g.coords)),
        }) for t, f, k, mt, mn, g in zip(
            twoway.t_jnctid.values,
            twoway.f_jnctid.values,
            twoway.id,
            twoway.meters.values,
            twoway.minutes.values,
            twoway.wkb_geometry.values,
        )
    ]
    twoway_edges_ft = [
        (f, t, k, {
            'meters': mt,
            'minutes': mn,
            'geom': g,
        }) for t, f, k, mt, mn, g in zip(
            twoway.t_jnctid.values,
            twoway.f_jnctid.values,
            twoway.id,
            twoway.meters.values,
            twoway.minutes.values,
            twoway.wkb_geometry.values,
        )
    ]
    oneway_edges_ft = [
        (f, t, k, {
            'meters': mt,
            'minutes': mn,
            'geom': g,
        }) for t, f, k, mt, mn, g in zip(
            oneway_ft.t_jnctid.values,
            oneway_ft.f_jnctid.values,
            oneway_ft.id,
            oneway_ft.meters.values,
            oneway_ft.minutes.values,
            oneway_ft.wkb_geometry.values,
        )
    ]
    oneway_edges_tf = [
        (t, f, -k, {
            'meters': mt,
            'minutes': mn,
            'geom': LineString(reversed(g.coords)),
        }) for t, f, k, mt, mn, g in zip(
            oneway_tf.t_jnctid.values,
            oneway_tf.f_jnctid.values,
            oneway_tf.id,
            oneway_tf.meters.values,
            oneway_tf.minutes.values,
            oneway_tf.wkb_geometry.values,
        )
    ]

    flats = {nid: lat for nid, lat in zip(gdf.f_jnctid.values, gdf.f_lat)}
    flons = {nid: lon for nid, lon in zip(gdf.f_jnctid.values, gdf.f_lon)}
    tlats = {nid: lat for nid, lat in zip(gdf.t_jnctid.values, gdf.t_lat)}
    tlons = {nid: lon for nid, lon in zip(gdf.t_jnctid.values, gdf.t_lon)}

    G = nx.MultiDiGraph()
    G.add_edges_from(twoway_edges_tf)
    G.add_edges_from(twoway_edges_ft)
    G.add_edges_from(oneway_edges_ft)
    G.add_edges_from(oneway_edges_tf)

    nx.set_node_attributes(G, flats, "lat")
    nx.set_node_attributes(G, flons, "lon")
    nx.set_node_attributes(G, tlats, "lat")
    nx.set_node_attributes(G, tlons, "lon")

    lats = [d['lat'] for _, d in G.nodes(data=True)]
    lons = [d['lon'] for _, d in G.nodes(data=True)]

    transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)

    proj_lats, proj_lons = transformer.transform(lats, lons)

    x = {nid: x for nid, x in zip(G.nodes(), proj_lats)}
    y = {nid: y for nid, y in zip(G.nodes(), proj_lons)}

    nx.set_node_attributes(G, x, "x")
    nx.set_node_attributes(G, y, "y")

    G = nx.MultiDiGraph(G.subgraph(max(nx.strongly_connected_components(G), key=len)))

    return G
