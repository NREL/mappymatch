from __future__ import annotations

from typing import NamedTuple

from pyproj import Transformer, CRS
from shapely.geometry import Point

from yamm.utils.crs import LATLON_CRS, XY_CRS


class Coordinate(NamedTuple):
    """
    coordinate a CRS and a geometry
    """

    geom: Point
    crs: CRS

    @classmethod
    def from_latlon(cls, lat: float, lon: float) -> Coordinate:
        """
        build a coordinate from only latitude and longitude

        :param lat:
        :param lon:

        :return:
        """
        return Coordinate(geom=Point(lon, lat), crs=LATLON_CRS)

    @classmethod
    def from_xy(cls, x: float, y: float) -> Coordinate:
        """
        build a coordinate from only x and y

        :param x:
        :param y:

        :return:
        """
        return Coordinate(geom=Point(x, y), crs=XY_CRS)

    @property
    def x(self) -> float:
        return self.geom.x

    @property
    def y(self) -> float:
        return self.geom.y

    def to_crs(self, new_crs: CRS) -> Coordinate:
        transformer = Transformer.from_crs(self.crs, new_crs)
        new_x, new_y = transformer.transform(self.geom.x, self.geom.y)

        return Coordinate(geom=Point(new_x, new_y), crs=new_crs)
