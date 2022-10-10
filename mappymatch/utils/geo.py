from typing import Tuple

from pyproj import Transformer

from mappymatch.constructs.coordinate import Coordinate
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
