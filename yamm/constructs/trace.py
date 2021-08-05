from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from pyproj import CRS, Transformer

from yamm.constructs.coordinate import Coordinate
from yamm.utils.crs import LATLON_CRS, XY_CRS

valid_latitude_names = {'latitude', 'Latitude', 'lat', 'Lat', "Latitude [degrees]"}
valid_longitude_names = {'longitude', 'Longitude', 'Lon', 'Lon', 'long', 'Long', "Longitude [degrees]"}


class Trace:
    coords: List[Coordinate]
    crs: CRS

    def __init__(self, coords: List[Coordinate], crs: CRS = XY_CRS):
        self.coords = coords
        self.crs = crs

    def __getitem__(self, i):
        new_coords = self.coords[i]
        if isinstance(new_coords, Coordinate):
            new_coords = [new_coords]

        return Trace(new_coords, self.crs)

    def __add__(self, other: Trace) -> Trace:
        new_coords = self.coords + other.coords
        return Trace(new_coords, self.crs)

    def __len__(self):
        return len(self.coords)

    @classmethod
    def from_dataframe(
            cls,
            dataframe: pd.DataFrame,
            xy: bool = True,
            lat_column: str = "latitude",
            lon_column: str = "longitude",
    ) -> Trace:
        """
        Builds a trace from a pandas dataframe

        Expects the dataframe to have latitude / longitude information in the epsg 4326 format

        Automatically projects each coordinate to epsg 3857 as well

        :param dataframe: pandas dataframe with _one_ trace
        :param lat_column: which column to use for latitude
        :param lon_column: which column to use for longitude
        :param xy: should the trace be projected to epsg 3857?

        :return: the trace built from the dataframe
        """
        lats = dataframe[lat_column]
        lons = dataframe[lon_column]
        if xy:
            transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)
            lat_proj, lon_proj = transformer.transform(lats, lons)
            coords = [Coordinate.from_xy(x, y) for x, y in zip(lat_proj, lon_proj)]
            crs = XY_CRS
        else:
            coords = [Coordinate.from_latlon(lat, lon) for lat, lon in zip(lats, lons)]
            crs = LATLON_CRS

        return Trace(coords, crs)

    @classmethod
    def from_csv(
            cls,
            file: Union[str, Path],
            xy: bool = True,
            lat_column: str = 'latitude',
            lon_column: str = 'longitude',
    ) -> Trace:
        """
        Builds a trace from a csv file.

        Expects the file to have latitude / longitude information in the epsg 4326 format

        Automatically projects each coordinate to epsg 3857 as well

        :param file: the file to load
        :param xy: should the trace be projected to x, y?
        :param lat_column: the name of the latitude column
        :param lon_column: the name of the longitude column

        :return: the trace
        """
        filepath = Path(file)
        if not filepath.is_file():
            raise FileNotFoundError(file)
        elif not filepath.suffix == ".csv":
            raise TypeError(f"file of type {filepath.suffix} does not appear to be a csv file")

        df = pd.read_csv(filepath)

        return Trace.from_dataframe(df, xy, lat_column, lon_column)

    def downsample(self, npoints: int) -> Trace:
        new_coords = [self.coords[0]] + [self.coords[i] for i in
                                         np.linspace(1, len(self.coords) - 1, npoints - 2).astype(int)] + [
                         self.coords[-1]]

        return Trace(new_coords, self.crs)

    def to_crs(self, new_crs: CRS) -> Trace:
        """
        converts the crs of a trace to a new crs

        :param new_crs: the crs to convert the trace to
        :return: the new trace
        """
        transformer = Transformer.from_crs(self.crs, new_crs)

        if self.crs == LATLON_CRS:
            x = [c.y for c in self.coords]
            y = [c.x for c in self.coords]
        else:
            x = [c.x for c in self.coords]
            y = [c.y for c in self.coords]

        new_x, new_y = transformer.transform(x, y)

        if new_crs == XY_CRS:
            new_coords = [Coordinate.from_xy(x, y) for x, y in zip(new_x, new_y)]
        elif new_crs == LATLON_CRS:
            new_coords = [Coordinate.from_latlon(x, y) for x, y in zip(new_x, new_y)]
        else:
            raise ValueError("incompatible crs to convert to")

        return Trace(coords=new_coords, crs=new_crs)
