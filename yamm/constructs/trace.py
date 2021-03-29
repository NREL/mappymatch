from __future__ import annotations

from csv import DictReader
from pathlib import Path
from typing import List

import numpy as np
from pyproj import CRS, Transformer

from yamm.constructs.coordinate import Coordinate
from yamm.utils.crs import LATLON_CRS, XY_CRS

valid_latitude_names = {'latitude', 'Latitude', 'lat', 'Lat', "Latitude [degrees]"}
valid_longitude_names = {'longitude', 'Longitude', 'Lon', 'Lon', 'long', 'Long', "Longitude [degrees]"}


class Trace:
    def __init__(self, coords: List[Coordinate], crs: CRS = XY_CRS):
        if any(map(lambda c: c.crs != crs, coords)):
            raise TypeError(f"CRS of the coordinates no not match CRS of the trace ({crs.to_epsg()})")

        self.coords = coords
        self.crs = crs

    def __getitem__(self, i):
        new_coords = self.coords[i]
        if isinstance(new_coords, Coordinate):
            new_coords = [new_coords]

        new_coords
        return Trace(new_coords, self.crs)

    def __add__(self, other: Trace) -> Trace:
        new_coords = self.coords + other.coords
        return Trace(new_coords, self.crs)

    def __len__(self):
        return len(self.coords)

    @classmethod
    def from_csv(cls, file: str, xy: bool = True) -> Trace:
        """
        Builds a trace from a csv file.

        Expects the file to have latitude / longitude information in the epsg 4326 format

        Automatically projects each coordinate to epsg 3857 as well

        :param file: the file to load
        :param xy: should the trace be projected to x, y?

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

            if len(lat_name_set) == 0:
                raise ValueError(f"could not find latitude information from fields {set(reader.fieldnames)}")
            elif len(lat_name_set) > 1:
                raise ValueError("found multiple instances of latitude; please only provide one")
            else:
                lat_name = list(lat_name_set)[0]

            if len(lon_name_set) == 0:
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

        return Trace(coords, crs)

    def downsample(self, npoints: int) -> Trace:
        coords = self.coords
        new_coords = [coords[0]] + [coords[i] for i in np.linspace(1, len(coords) - 1, npoints - 2).astype(int)] + [
            coords[-1]]
        self.coords = new_coords

        return self
