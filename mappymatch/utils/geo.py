from typing import Tuple

from pyproj import CRS, Transformer
from shapely.geometry import LineString
from shapely.ops import transform

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.road import Road
from mappymatch.constructs.trace import Trace
from mappymatch.utils.crs import LATLON_CRS, XY_CRS


def xy_to_latlon(x: float, y: float) -> Tuple[float, float]:
    """
    Tramsform x,y coordinates to lat and lon

    Args:
        x: X.
        y: Y.

    Returns:
    Transformed lat and lon as lat, lon.
    """
    transformer = Transformer.from_crs(XY_CRS, LATLON_CRS)
    lat, lon = transformer.transform(x, y)

    return lat, lon


def latlon_to_xy(lat: float, lon: float) -> Tuple[float, float]:
    """
    Tramsform lat,lon coordinates to x and y.

    Args:
        lat: The latitude.
        lon: The longitude.

    Returns:
    Transformed x and y as x, y.
    """
    transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)
    x, y = transformer.transform(lat, lon)

    return x, y


def geofence_from_trace(
    trace: Trace,
    padding: float = 15,
    crs: CRS = LATLON_CRS,
    buffer_res: int = 2,
) -> Geofence:
    """
    Computes a bounding box surrounding a trace.

    The calculation is done using  the minimum and maximum x and y

    TODO: maintainer check.

    Args:
    trace: The trace to compute the bounding box for.
    padding: The padding (in meters) to add to the box.
    crs: should the geofence be projected to xy???
    buffer_res: should the geofence be projected to xy???

    Returns:
        The computed bounding box.
    """

    trace_line_string = LineString([c.geom for c in trace.coords])

    polygon = trace_line_string.buffer(padding, buffer_res)

    if trace.crs != crs:
        project = Transformer.from_crs(
            trace.crs, crs, always_xy=True
        ).transform
        polygon = transform(project, polygon)
        return Geofence(crs=crs, geometry=polygon)

    return Geofence(crs=trace.crs, geometry=polygon)


def road_to_coord_dist(road: Road, coord: Coordinate) -> float:
    """
    Compute the distance between a coordinate and a road.

    TODO: Maintainer check.

    Args:
    road: The road object.
    coord: The coordinate object.

    Returns:
        The distance in ?
    """

    dist = coord.geom.distance(road.geom)

    return dist


def coord_to_coord_dist(a: Coordinate, b: Coordinate) -> float:
    """
    Compute the distance between to coordinates.

    TODO: maintainer check

    Args:
        a: The starting coordinate?
        b: The ending coordinate?

    Returns:
        The distance in ?
    """
    dist = a.geom.distance(b.geom)

    return dist
