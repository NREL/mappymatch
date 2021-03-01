from __future__ import annotations

from typing import NamedTuple, Optional

from pyproj import CRS, Transformer


class Coordinate(NamedTuple):
    """
    coordinate with epsg 4326 representation and optional epsg 3857 representation
    """

    # epsg 4326
    lat: float
    lon: float

    # epsg 3857
    x: Optional[float] = None
    y: Optional[float] = None

    def project_xy(self) -> Coordinate:
        base_crs = CRS(4326)
        xy_crs = CRS(3857)
        transformer = Transformer.from_crs(base_crs, xy_crs)
        x, y = transformer.transform(self.lat, self.lon)
        return Coordinate(lat=self.lat, lon=self.lon, x=x, y=y)
