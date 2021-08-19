from __future__ import annotations

from typing import NamedTuple, Any

from pyproj import Transformer, CRS
from shapely.geometry import Point

CoordinateId: Any


class Coordinate(NamedTuple):
    """
    coordinate a CRS and a geometry
    """

    coordinate_id: CoordinateId
    geom: Point
    crs: CRS

    def __repr__(self):
        return f"Coordinate(coordinate_id={self.coordinate_id}, x={self.x}, y={self.y}, crs={self.crs.to_authority()})"

    @property
    def x(self) -> float:
        return self.geom.x

    @property
    def y(self) -> float:
        return self.geom.y

    def to_crs(self, new_crs: CRS) -> Coordinate:
        transformer = Transformer.from_crs(self.crs, new_crs)
        new_x, new_y = transformer.transform(self.geom.x, self.geom.y)

        return Coordinate(coordinate_id=self.coordinate_id, geom=Point(new_x, new_y), crs=new_crs)
