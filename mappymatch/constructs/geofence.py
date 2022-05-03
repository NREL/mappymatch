from pathlib import Path
from typing import NamedTuple, Union

from geopandas import read_file
from pyproj import CRS
from shapely.geometry import Polygon


class Geofence(NamedTuple):
    crs: CRS
    geometry: Polygon

    @classmethod
    def from_geojson(cls, file: Union[Path, str]) -> Geofence:
        filepath = Path(file)
        frame = read_file(filepath)

        if len(frame) > 1:
            raise TypeError(
                "found multiple polygons in the input; please only provide one"
            )
        elif frame.crs is None:
            raise TypeError(
                "no crs information found in the file; please make sure file has a crs"
            )

        polygon = frame.iloc[0].geometry

        return Geofence(crs=frame.crs, geometry=polygon)
