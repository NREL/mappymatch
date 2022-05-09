from __future__ import annotations

import math
from typing import Any, NamedTuple

from pyproj import CRS, Transformer
from shapely.geometry import Point

from mappymatch.utils.crs import LATLON_CRS

CoordinateId: Any


class Coordinate(NamedTuple):
    """
    coordinate a CRS and a geometry
    """

    coordinate_id: CoordinateId
    geom: Point
    crs: CRS

    def __repr__(self):
        crs_a = self.crs.to_authority() if self.crs else "Null"
        return f"Coordinate(coordinate_id={self.coordinate_id}, x={self.x}, y={self.y}, crs={crs_a})"

    @classmethod
    def from_lat_lon(cls, lat: float, lon: float) -> Coordinate:
        """
        build a coordinate from a latitude/longitude

        :param lat the latitude
        :param lon the longitude

        :return: the coordinate
        """
        return cls(coordinate_id=None, geom=Point(lon, lat), crs=LATLON_CRS)

    @property
    def x(self) -> float:
        return self.geom.x

    @property
    def y(self) -> float:
        return self.geom.y

    def to_crs(self, new_crs: CRS) -> Coordinate:
        new_x: float
        new_y: float
        transformer: Transformer
        transformer = Transformer.from_crs(self.crs, new_crs)
        new_x, new_y = transformer.transform(self.geom.y, self.geom.x)

        if math.isinf(new_x) or math.isinf(new_y):
            raise ValueError(
                f"Unable to convert {self.crs} ({self.geom.x}, {self.geom.y}) -> {new_crs} ({new_x}, {new_y})"
            )

        return Coordinate(
            coordinate_id=self.coordinate_id,
            geom=Point(new_x, new_y),
            crs=new_crs,
        )
