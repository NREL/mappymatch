from typing import Tuple

from pyproj import CRS, Transformer
from shapely.geometry import LineString
from shapely.ops import transform

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.geofence import Geofence
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
    Computes a bounding polygon surrounding a trace.

    This is done by computing a radial buffer around the entire trace (as a line).

    Args:
        trace: The trace to compute the bounding polygon for.
        padding: The padding (in meters) around the trace line.
        crs: The coordinate reference system to use.
        buffer_res: The resolution of the surrounding buffer.

    Returns:
        The computed bounding polygon.
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


def coord_to_coord_dist(a: Coordinate, b: Coordinate) -> float:
    """
    Compute the distance between two coordinates.

    Args:
        a: The first coordinate
        b: The second coordinate

    Returns:
        The distance in meters
    """
    dist = a.geom.distance(b.geom)

    return dist
