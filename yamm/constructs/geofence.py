from typing import NamedTuple

from pyproj import CRS
from shapely.geometry import Polygon


class Geofence(NamedTuple):
    crs: CRS
    geometry: Polygon
