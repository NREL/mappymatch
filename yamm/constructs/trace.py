from __future__ import annotations

from csv import DictReader
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
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
    def from_csv(
            cls,
            file: Union[str, Path],
            xy: bool = True,
            lat_column: Optional[str] = None,
            lon_column: Optional[str] = None,
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

        lats = []
        lons = []
        with filepath.open('r') as f:
            reader = DictReader(f)

            lat_name_set = valid_latitude_names.intersection(set(reader.fieldnames))
            lon_name_set = valid_longitude_names.intersection(set(reader.fieldnames))

            if lat_column:
                lat_name = lat_column
            elif len(lat_name_set) == 0:
                raise ValueError(f"could not find latitude information from fields {set(reader.fieldnames)}")
            elif len(lat_name_set) > 1:
                raise ValueError("found multiple instances of latitude; please only provide one")
            else:
                lat_name = list(lat_name_set)[0]

            if lon_column:
                lon_name = lon_column
            elif len(lon_name_set) == 0:
                raise ValueError(f"could not find longitude information from fields {set(reader.fieldnames)}")
            elif len(lon_name_set) > 1:
                raise ValueError("found multiple instances of longitude; please only provide one")
            else:
                lon_name = list(lon_name_set)[0]

            for row in reader:
                lats.append(float(row[lat_name]))
                lons.append(float(row[lon_name]))

        if xy:
            transformer = Transformer.from_crs(LATLON_CRS, XY_CRS)

            lat_proj, lon_proj = transformer.transform(lats, lons)

            coords = [Coordinate.from_xy(x, y) for x, y in zip(lat_proj, lon_proj)]
            crs = XY_CRS
        else:
            coords = [Coordinate.from_latlon(lat, lon) for lat, lon in zip(lats, lons)]
            crs = LATLON_CRS

        trace = Trace(
            coords=coords,
            crs=crs
        )

        return trace

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
