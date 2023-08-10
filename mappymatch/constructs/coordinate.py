from __future__ import annotations

import math
from typing import Any, NamedTuple

from pyproj import CRS, Transformer
from pyproj.exceptions import ProjError
from shapely.geometry import Point

from mappymatch.utils.crs import LATLON_CRS


class Coordinate(NamedTuple):
    """
    Represents a single coordinate with a CRS and a geometry

    Attributes:
        coordinate_id: The unique identifier for this coordinate
        geom: The geometry of this coordinate
        crs: The CRS of this coordinate
        x: The x value of this coordinate
        y: The y value of this coordinate
    """

    coordinate_id: Any
    geom: Point
    crs: CRS

    def __repr__(self):
        crs_a = self.crs.to_authority() if self.crs else "Null"
        return f"Coordinate(coordinate_id={self.coordinate_id}, x={self.x}, y={self.y}, crs={crs_a})"

    @classmethod
    def from_lat_lon(cls, lat: float, lon: float) -> Coordinate:
        """
        Build a coordinate from a latitude/longitude

        Args:
            lat: The latitude
            lon: The longitude

        Returns:
            A new coordinate
        """
        return cls(coordinate_id=None, geom=Point(lon, lat), crs=LATLON_CRS)

    @property
    def x(self) -> float:
        return self.geom.x

    @property
    def y(self) -> float:
        return self.geom.y

    def to_crs(self, new_crs: Any) -> Coordinate:
        """
        Convert this coordinate to a new CRS

        Args:
            new_crs: The new CRS to convert to

        Returns:
            A new coordinate with the new CRS

        Raises:
            A ValueError if it fails to convert the coordinate
        """
        # convert the incoming crs to an pyproj.crs.CRS object; this could fail
        try:
            new_crs = CRS(new_crs)
        except ProjError as e:
            raise ValueError(
                f"Could not parse incoming `new_crs` parameter: {new_crs}"
            ) from e

        if new_crs == self.crs:
            return self

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
