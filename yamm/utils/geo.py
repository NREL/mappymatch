from typing import Tuple

from pyproj import Transformer
from shapely.geometry import LineString
from shapely.ops import transform

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.geofence import Geofence
from yamm.constructs.road import Road
from yamm.constructs.trace import Trace
from yamm.utils.crs import XY_CRS, LATLON_CRS


def xy_to_latlon(x: float, y: float) -> Tuple[float, float]:
    transformer = Transformer.from_crs(XY_CRS, LATLON_CRS)
    lat, lon = transformer.transform(x, y)

    return lat, lon


def latlon_to_xy(lat: float, lon: float) -> Tuple[float, float]:
    transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)
    x, y = transformer.transform(lat, lon)

    return x, y


def geofence_from_trace(trace: Trace, padding: float = 15, xy: bool = False, buffer_res: int = 2) -> Geofence:
    """
    computes a bounding box surrounding a trace by taking the minimum and maximum x and y

    :param trace: the trace to compute the bounding box for
    :param padding: how much padding (in meters) to add to the box
    :param xy: should the geofence be projected to xy?
    :param buffer_res: should the geofence be projected to xy?

    :return: the computed bounding box
    """

    if trace.crs != XY_CRS:
        trace = trace.to_crs(XY_CRS)

    trace_line_string = LineString([c.geom for c in trace.coords])

    polygon = trace_line_string.buffer(padding, buffer_res)

    if xy:
        return Geofence(crs=XY_CRS, geometry=polygon)

    project = Transformer.from_crs(XY_CRS, LATLON_CRS, always_xy=True).transform
    polygon = transform(project, polygon)

    return Geofence(crs=LATLON_CRS, geometry=polygon)


def road_to_coord_dist(road: Road, coord: Coordinate) -> float:
    """
    helper function to compute the distance between a coordinate and a road

    :param road: the road object
    :param coord: the coordinate object

    :return: the distance
    """

    dist = coord.geom.distance(road.geom)

    return dist


def coord_to_coord_dist(a: Coordinate, b: Coordinate):
    """
    helper function to compute the distance between to coordinates

    :param a: coordinate a
    :param b: coordinate b

    :return: the distance
    """
    dist = a.geom.distance(b.geom)

    return dist
