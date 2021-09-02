from typing import Tuple

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from yamm.constructs.geofence import Geofence
from yamm.constructs.trace import Trace
from yamm.utils.crs import LATLON_CRS


def get_tsdc_trace(trip_id, table, engine) -> Tuple[Trace, pd.DataFrame]:
    q = f"""
    select * from {table}  
    where trip_id='{trip_id}'
    order by time_rel
    """
    try:
        raw_trip_gdf = gpd.GeoDataFrame.from_postgis(q, engine)
        trip_gdf = raw_trip_gdf.set_index(['point_id', 'time_rel'])
        return Trace.from_geo_dataframe(trip_gdf), raw_trip_gdf
    except ValueError:
        # table might not have geometry
        raw_trip_df = pd.read_sql(q, engine)
        trip_df = raw_trip_df.set_index(['point_id', 'time_local'])
        return Trace.from_dataframe(trip_df, lat_column="latitude", lon_column="longitude"), raw_trip_df


def compute_bbox_from_table(table, padding, engine):
    q = f"""
    select min(latitude) as lat_min, max(latitude) as lat_max,
    min(longitude) as lon_min, max(longitude) as lon_max
    from {table} 
    """
    df = pd.read_sql(q, engine)
    b = df.iloc[0]

    bbox = box(b.lon_min - padding, b.lat_min - padding, b.lon_max + padding, b.lat_max + padding)

    return Geofence(geometry=bbox, crs=LATLON_CRS)


def get_unique_trips(table, engine):
    q = f"""
    select distinct trip_id from {table} 
    """
    trips = pd.read_sql(q, engine)
    trips['table'] = table

    return trips


