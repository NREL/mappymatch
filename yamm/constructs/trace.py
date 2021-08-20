from __future__ import annotations

from pathlib import Path
from typing import List, Union, Optional

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame, points_from_xy, read_file
from pyproj import CRS

from yamm.constructs.coordinate import Coordinate
from yamm.utils.crs import LATLON_CRS, XY_CRS

valid_latitude_names = {'latitude', 'Latitude', 'lat', 'Lat', "Latitude [degrees]"}
valid_longitude_names = {'longitude', 'Longitude', 'Lon', 'Lon', 'long', 'Long', "Longitude [degrees]"}


class Trace:
    _frame: GeoDataFrame

    coords: List[Coordinate]
    crs: CRS

    def __init__(self, frame: GeoDataFrame):
        self._frame = frame

    def __getitem__(self, i):
        if isinstance(i, int):
            i = [i]
        new_frame = self._frame.iloc[i]
        return Trace(new_frame)

    def __add__(self, other: Trace) -> Trace:
        if self.crs != other.crs:
            raise TypeError(f"cannot add two traces together with different crs")
        new_frame = self._frame.append(other._frame)
        return Trace(new_frame)

    def __len__(self):
        return len(self._frame)

    @property
    def index(self) -> pd.Index:
        return self._frame.index

    @property
    def coords(self) -> List[Coordinate]:
        coords = [Coordinate(i, g, self.crs) for i, g in zip(self._frame.index, self._frame.geometry)]
        return coords

    @property
    def crs(self) -> CRS:
        return self._frame.crs

    @classmethod
    def from_coords(cls, coords: List[Coordinate]) -> Trace:
        frame = GeoDataFrame([{'geometry': c.geom} for c in coords], crs=coords[0].crs)
        frame.crs = coords[0].crs
        return Trace(frame)

    @classmethod
    def from_geo_dataframe(
            cls,
            frame: GeoDataFrame,
            xy: bool = True,
    ) -> Trace:
        """
        Builds a trace from a pandas dataframe

        Expects the dataframe to have latitude / longitude information in the epsg 4326 format

        Automatically projects each coordinate to epsg 3857 as well

        :param frame: geopandas dataframe with _one_ trace
        :param xy: should the trace be projected to epsg 3857?

        :return: the trace built from the dataframe
        """
        # get rid of any extra info besides geometry and index
        frame = GeoDataFrame(geometry=frame.geometry, index=frame.index)
        if xy:
            frame = frame.to_crs(XY_CRS)

        return Trace(frame)

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
        frame = GeoDataFrame(
            geometry=points_from_xy(dataframe[lon_column], dataframe[lat_column]),
            index=dataframe.index,
            crs=LATLON_CRS,
        )
        if xy:
            frame = frame.to_crs(XY_CRS)

        return Trace(frame)

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

    @classmethod
    def from_geojson(
            cls,
            file: Union[str, Path],
            index_property: Optional[str] = None,
            xy: bool = True
    ):
        filepath = Path(file)
        frame = read_file(filepath)
        if index_property in frame.columns:
            frame = frame.set_index(index_property)

        if xy:
            frame = frame.to_crs(XY_CRS)

        return Trace(frame)

    def downsample(self, npoints: int) -> Trace:
        s = list(np.linspace(0, len(self._frame) - 1, npoints).astype(int))

        new_frame = self._frame.iloc[s]

        return Trace(new_frame)

    def drop(self, index=List) -> Trace:
        """
        remove points from the trace specified by the index parameter

        :param index: the index of points to drop (0 based index)

        :return: the trace with the points removed
        """
        new_frame = self._frame.drop(index)

        return Trace(new_frame)

    def to_crs(self, new_crs: CRS) -> Trace:
        """
        converts the crs of a trace to a new crs

        :param new_crs: the crs to convert the trace to
        :return: the new trace
        """
        new_frame = self._frame.to_crs(new_crs)
        return Trace(new_frame)
