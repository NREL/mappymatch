from __future__ import annotations

from typing import NamedTuple

from pyproj import CRS, Transformer

LATLON_CRS = CRS(4326)
XY_CRS = CRS(3857)


class Coordinate(NamedTuple):
    """
    coordinate with epsg 4326 representation and epsg 3857 representation
    """

    # epsg 4326
    lat: float
    lon: float

    # epsg 3857
    x: float
    y: float

    @classmethod
    def from_latlon(cls, lat: float, lon: float) -> Coordinate:
        """
        build a coordinate from only latitude and longitude

        :param lat:
        :param lon:

        :return:
        """
        transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)
        x, y = transformer.transform(lat, lon)

        return Coordinate(lat=lat, lon=lon, x=x, y=y)

    @classmethod
    def from_xy(cls, x: float, y: float) -> Coordinate:
        """
        build a coordinate from only x and y

        :param x:
        :param y:

        :return:
        """
        transformer = Transformer.from_crs(XY_CRS, LATLON_CRS)
        lon, lat = transformer.transform(x, y)

        return Coordinate(lat=lat, lon=lon, x=x, y=y)
