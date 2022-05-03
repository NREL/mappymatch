from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import List, Union, Optional, Set
import re

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame, points_from_xy, read_file, read_parquet
from pyproj import CRS

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from mappymatch.utils.geohash import encode


class Trace:
    _frame: GeoDataFrame

    coords_list: List[Coordinate]

    def __init__(self, frame: GeoDataFrame):
        self._frame = frame

    def __getitem__(self, i) -> Trace:
        if isinstance(i, int):
            i = [i]
        new_frame = self._frame.iloc[i]
        return Trace(new_frame)

    def __add__(self, other: Trace) -> Trace:
        if self.crs != other.crs:
            raise TypeError(f"cannot add two traces together with different crs")
        new_frame = pd.concat([self._frame, other._frame])
        return Trace(new_frame)

    def __len__(self):
        return len(self._frame)

    @property
    def index(self) -> pd.Index:
        return self._frame.index

    @cached_property
    def coords(self) -> List[Coordinate]:
        coords_list = [
            Coordinate(i, g, self.crs)
            for i, g in zip(self._frame.index, self._frame.geometry)
        ]
        return coords_list

    def geohashes(self, precision=12) -> Set[str]:
        """
        returns a set of the geohashes that this trace intersects
        """
        if self.crs != LATLON_CRS:
            frame = self._frame.to_crs(LATLON_CRS)
        else:
            frame = self._frame

        geohashes = set(
            frame.geometry.apply(lambda g: encode(g.y, g.x, precision)).unique()
        )

        return geohashes

    @property
    def crs(self) -> CRS:
        return self._frame.crs

    @classmethod
    def build(cls, frame: GeoDataFrame, xy: bool = True) -> Trace:
        """
        build a new trace
        """
        if xy:
            frame = frame.to_crs(XY_CRS)
        return Trace(frame)

    @classmethod
    def from_geo_dataframe(
        cls,
        frame: GeoDataFrame,
        xy: bool = True,
    ) -> Trace:
        """
        Builds a trace from a geopandas dataframe

        Expects the dataframe to have geometry column

        :param frame: geopandas dataframe with _one_ trace
        :param xy: should the trace be projected to epsg 3857?

        :return: the trace built from the dataframe
        """
        # get rid of any extra info besides geometry and index
        frame = GeoDataFrame(geometry=frame.geometry, index=frame.index)
        return Trace.build(frame, xy)

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

        return Trace.build(frame, xy)

    @classmethod
    def from_gpx(
        cls,
        file: Union[str, Path],
        xy: bool = True,
    ) -> Trace:
        """
        Builds a trace from a gpx file.

        Expects the file to have simple gpx structure: a sequence of lat, lon pairs

        :param file: the file to load
        :param xy: should the trace be projected to x, y?
        :return: the trace
        """
        filepath = Path(file)
        if not filepath.is_file():
            raise FileNotFoundError(file)
        elif not filepath.suffix == ".gpx":
            raise TypeError(
                f"file of type {filepath.suffix} does not appear to be a gpx file"
            )
        data = open(filepath).read()

        lat_column, lon_column = "lat", "lon"
        lat = np.array(re.findall(r'lat="([^"]+)',data),dtype=float)
        lon = np.array(re.findall(r'lon="([^"]+)',data),dtype=float)
        df = pd.DataFrame(zip(lat, lon), columns=[lat_column, lon_column])
        return Trace.from_dataframe(df, xy, lat_column, lon_column)

    @classmethod
    def from_csv(
        cls,
        file: Union[str, Path],
        xy: bool = True,
        lat_column: str = "latitude",
        lon_column: str = "longitude",
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
            raise TypeError(
                f"file of type {filepath.suffix} does not appear to be a csv file"
            )

        columns = pd.read_csv(filepath, nrows=0).columns.to_list()
        if lat_column in columns and lon_column in columns:
            df = pd.read_csv(filepath)
            return Trace.from_dataframe(df, xy, lat_column, lon_column)
        else:
            raise ValueError(
                "Could not find any geometry information in the file; "
                "Make sure there are latitude and longitude columns "
                "[and provide the lat/lon column names to this function]"
            )

    @classmethod
    def from_parquet(cls, file: Union[str, Path], xy: bool = True):
        """
        read a trace from a parquet file

        :param file:
        :param xy:
        :return:
        """
        filepath = Path(file)
        frame = read_parquet(filepath)

        return Trace.build(frame, xy)

    @classmethod
    def from_geojson(
        cls,
        file: Union[str, Path],
        index_property: Optional[str] = None,
        xy: bool = True,
    ):
        """
        reads a geojson file; if index_property is not specified, this will set any property columns as the index.

        :param file:
        :param index_property:
        :param xy:
        :return:
        """
        filepath = Path(file)
        frame = read_file(filepath)
        if index_property and index_property in frame.columns:
            frame = frame.set_index(index_property)
        else:
            gname = frame.geometry.name
            index_cols = [c for c in frame.columns if c != gname]
            frame = frame.set_index(index_cols)

        return Trace.build(frame, xy)

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

    def to_geojson(self, file: Union[str, Path]):
        """
        write the trace to a csv file

        :param file:
        :return:
        """
        self._frame.to_file(file, driver="GeoJSON")
