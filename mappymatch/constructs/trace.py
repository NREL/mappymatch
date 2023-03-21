from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame, points_from_xy, read_file, read_parquet
from pyproj import CRS

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.utils.crs import LATLON_CRS, XY_CRS


class Trace:
    """
    A Trace is a collection of coordinates that represents a trajectory to be matched.

    Attributes:
        coords: A list of all the coordinates
        crs: The CRS of the trace
        index: The index of the trace
    """

    _frame: GeoDataFrame

    def __init__(self, frame: GeoDataFrame):
        if frame.index.has_duplicates:
            duplicates = frame.index[frame.index.duplicated()].values
            raise IndexError(
                f"Trace cannot have duplicates in the index but found {duplicates}"
            )
        self._frame = frame

    def __getitem__(self, i) -> Trace:
        if isinstance(i, int):
            i = [i]
        new_frame = self._frame.iloc[i]
        return Trace(new_frame)

    def __add__(self, other: Trace) -> Trace:
        if self.crs != other.crs:
            raise TypeError(
                "cannot add two traces together with different crs"
            )
        new_frame = pd.concat([self._frame, other._frame])
        return Trace(new_frame)

    def __len__(self):
        """Number of coordinate pairs."""
        return len(self._frame)

    def __str__(self):
        output_lines = [
            "Mappymatch Trace object",
            f'coords: {self.coords if hasattr(self, "coords") else None}',
            f"frame: {self._frame}",
        ]
        return "\n".join(output_lines)

    def __repr__(self):
        return self.__str__()

    @property
    def index(self) -> pd.Index:
        """Get index to underlying GeoDataFrame."""
        return self._frame.index

    @cached_property
    def coords(self) -> List[Coordinate]:
        """
        Get coordinates as Coordinate objects.
        """
        coords_list = [
            Coordinate(i, g, self.crs)
            for i, g in zip(self._frame.index, self._frame.geometry)
        ]
        return coords_list

    @property
    def crs(self) -> CRS:
        """Get Coordinate Reference System(CRS) to underlying GeoDataFrame."""
        return self._frame.crs

    @classmethod
    def from_geo_dataframe(
        cls,
        frame: GeoDataFrame,
        xy: bool = True,
    ) -> Trace:
        """
        Builds a trace from a geopandas dataframe

        Expects the dataframe to have geometry column

        Args:
            frame: geopandas dataframe with _one_ trace
            xy: should the trace be projected to epsg 3857?

        Returns:
            The trace built from the geopandas dataframe
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

        Args:
            dataframe: pandas dataframe with _one_ trace
            xy: should the trace be projected to epsg 3857?
            lat_column: the name of the latitude column
            lon_column: the name of the longitude column

        Returns:
            The trace built from the pandas dataframe
        """
        frame = GeoDataFrame(
            geometry=points_from_xy(
                dataframe[lon_column], dataframe[lat_column]
            ),
            index=dataframe.index,
            crs=LATLON_CRS,
        )

        return Trace.from_geo_dataframe(frame, xy)

    @classmethod
    def from_gpx(
        cls,
        file: Union[str, Path],
        xy: bool = True,
    ) -> Trace:
        """
        Builds a trace from a gpx file.

        Expects the file to have simple gpx structure: a sequence of lat, lon pairs

        Args:
            file: the gpx file
            xy: should the trace be projected to epsg 3857?

        Returns:
            The trace built from the gpx file
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
        lat = np.array(re.findall(r'lat="([^"]+)', data), dtype=float)
        lon = np.array(re.findall(r'lon="([^"]+)', data), dtype=float)
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

        Args:
            file: the csv file
            xy: should the trace be projected to epsg 3857?
            lat_column: the name of the latitude column
            lon_column: the name of the longitude column

        Returns:
            The trace built from the csv file
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
        Read a trace from a parquet file

        Args:
            file: the parquet file
            xy: should the trace be projected to epsg 3857?

        Returns:
            The trace built from the parquet file
        """
        filepath = Path(file)
        frame = read_parquet(filepath)

        return Trace.from_geo_dataframe(frame, xy)

    @classmethod
    def from_geojson(
        cls,
        file: Union[str, Path],
        index_property: Optional[str] = None,
        xy: bool = True,
    ):
        """
        Reads a trace from a geojson file;
        If index_property is not specified, this will set any property columns as the index.

        Args:
            file: the geojson file
            index_property: the name of the property to use as the index
            xy: should the trace be projected to epsg 3857?

        Returns:
            The trace built from the geojson file
        """
        filepath = Path(file)
        frame = read_file(filepath)
        if index_property and index_property in frame.columns:
            frame = frame.set_index(index_property)
        else:
            gname = frame.geometry.name
            index_cols = [c for c in frame.columns if c != gname]
            frame = frame.set_index(index_cols)

        return Trace.from_geo_dataframe(frame, xy)

    def downsample(self, npoints: int) -> Trace:
        """
        Downsample the trace to a given number of points

        Args:
            npoints: the number of points to downsample to

        Returns:
            The downsampled trace
        """
        s = list(np.linspace(0, len(self._frame) - 1, npoints).astype(int))

        new_frame = self._frame.iloc[s]

        return Trace(new_frame)

    def drop(self, index=List) -> Trace:
        """
        Remove points from the trace specified by the index parameter

        Args:
            index: the index of the points to drop (0 based index)

        Returns:
            The trace with the points removed
        """
        new_frame = self._frame.drop(index)

        return Trace(new_frame)

    def to_crs(self, new_crs: CRS) -> Trace:
        """
        Converts the crs of a trace to a new crs

        Args:
            new_crs: the new crs to convert to

        Returns:
            A new trace with the new crs
        """
        new_frame = self._frame.to_crs(new_crs)
        return Trace(new_frame)

    def to_geojson(self, file: Union[str, Path]):
        """
        Write the trace to a geojson file

        Args:
            file: the file to write to
        """
        self._frame.to_file(file, driver="GeoJSON")
