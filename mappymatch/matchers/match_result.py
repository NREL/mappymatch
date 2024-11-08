from dataclasses import dataclass
from typing import List, Optional

import geopandas as gpd
import numpy as np
import pandas as pd

from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road


@dataclass
class MatchResult:
    matches: List[Match]
    path: Optional[List[Road]] = None

    @property
    def crs(self):
        first_crs = self.matches[0].coordinate.crs
        if not all([first_crs.equals(m.coordinate.crs) for m in self.matches]):
            raise ValueError(
                "Found that there were different CRS within the matches. "
                "These must all be equal to use this function"
            )
        return first_crs

    def matches_to_geodataframe(self) -> gpd.GeoDataFrame:
        """
        Returns a geodataframe with all the coordinates and their resulting match (or NA if no match) in each row
        """
        df = self.matches_to_dataframe()
        gdf = gpd.GeoDataFrame(df, geometry="geom")

        if len(self.matches) == 0:
            return gdf

        gdf = gdf.set_crs(self.crs)

        return gdf

    def matches_to_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe with all the coordinates and their resulting match (or NA if no match) in each row.

        Returns:
            A pandas dataframe
        """
        df = pd.DataFrame([m.to_flat_dict() for m in self.matches])
        df = df.fillna(np.nan)

        return df

    def path_to_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe with the resulting estimated trace path through the road network.
        The dataframe is empty if there was no path.

        Returns:
            A pandas dataframe
        """
        if self.path is None:
            return pd.DataFrame()

        df = pd.DataFrame([r.to_flat_dict() for r in self.path])
        df = df.fillna(np.nan)

        return df

    def path_to_geodataframe(self) -> gpd.GeoDataFrame:
        """
        Returns a geodataframe with the resulting estimated trace path through the road network.
        The geodataframe is empty if there was no path.

        Returns:
            A geopandas geodataframe
        """
        if self.path is None:
            return gpd.GeoDataFrame()

        df = self.path_to_dataframe()
        gdf = gpd.GeoDataFrame(df, geometry="geom")

        gdf = gdf.set_crs(self.crs)

        return gdf
