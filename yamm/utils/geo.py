from __future__ import annotations

from typing import NamedTuple

valid_latitude_names = {'latitude', 'Latitude', 'lat', 'Lat'}
valid_longitude_names = {'longitude', 'Longitude', 'Lon', 'Lon', 'long', 'Long'}


class Coordinate(NamedTuple):
    lat: float
    lon: float

    @classmethod
    def from_dict(cls, d: dict) -> Coordinate:
        """
        attempt to parse from a dictionary

        :param d: the dict to parse from
        :return: a Coordinate
        """
        lat_name_set = valid_latitude_names.intersection(d.keys())
        lon_name_set = valid_longitude_names.intersection(d.keys())

        if len(lat_name_set) == 0:
            raise ValueError(f"could not find latitude information from fields {d.keys()}")
        elif len(lat_name_set) > 1:
            raise ValueError("found multiple instances of latitude; please only provide one")
        else:
            lat_name = list(lat_name_set)[0]

        if len(lon_name_set) == 0:
            raise ValueError(f"could not find longitude information from fields {d.keys()}")
        elif len(lon_name_set) > 1:
            raise ValueError("found multiple instances of longitude; please only provide one")
        else:
            lon_name = list(lon_name_set)[0]

        lat = d[lat_name]
        lon = d[lon_name]

        return Coordinate(lat=lat, lon=lon)
