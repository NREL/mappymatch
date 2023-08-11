from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road


@dataclass
class MatchResult:
    matches: List[Match]
    path: Optional[List[Road]] = None

    def matches_to_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe with all the coordinates and their resulting match (or NA if no match) in each row.

        Returns:
            A pandas dataframe
        """
        df = pd.DataFrame([m.to_flat_dict() for m in self.matches])
        df = df.fillna(np.NAN)

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
        df = df.fillna(np.NAN)

        return df
