from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from geopandas import read_file
from pyproj import CRS, Transformer
from shapely.geometry import LineString, Polygon, mapping
from shapely.ops import transform

from mappymatch.constructs.trace import Trace
from mappymatch.utils.crs import LATLON_CRS


class Geofence:
    """
    A geofence is basically a shapely polygon with a CRS

    Args:
        geom: The polygon geometry of the geofence
        crs: The CRS of the geofence
    """

    def __init__(self, crs: CRS, geometry: Polygon):
        self.crs = crs
        self.geometry = geometry

    @classmethod
    def from_geojson(cls, file: Union[Path, str]) -> Geofence:
        """
        Creates a new geofence from a geojson file.

        Args:
            file: The path to the geojson file

        Returns:
            A new geofence
        """
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

    @classmethod
    def from_trace(
        cls,
        trace: Trace,
        padding: float = 1e3,
        crs: CRS = LATLON_CRS,
        buffer_res: int = 2,
    ) -> Geofence:
        """
        Create a new geofence from a trace.

        This is done by computing a radial buffer around the
        entire trace (as a line).

        Args:
            trace: The trace to compute the bounding polygon for.
            padding: The padding (in meters) around the trace line.
            crs: The coordinate reference system to use.
            buffer_res: The resolution of the surrounding buffer.

        Returns:
            The computed bounding polygon.
        """

        trace_line_string = LineString([c.geom for c in trace.coords])

        # Add buffer to LineString.
        polygon = trace_line_string.buffer(padding, buffer_res)

        if trace.crs != crs:
            project = Transformer.from_crs(
                trace.crs, crs, always_xy=True
            ).transform
            polygon = transform(project, polygon)
            return Geofence(crs=crs, geometry=polygon)

        return Geofence(crs=trace.crs, geometry=polygon)

    def to_geojson(self) -> str:
        """
        Converts the geofence to a geojson string.
        """
        if self.crs != LATLON_CRS:
            transformer = Transformer.from_crs(self.crs, LATLON_CRS)
            geometry: Polygon = transformer.transform(self.geometry)  # type: ignore
        else:
            geometry = self.geometry

        return json.dumps(mapping(geometry))
