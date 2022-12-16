from dataclasses import dataclass
from typing import List, Optional

from mappymatch.constructs.match import Match
from mappymatch.constructs.road import Road


@dataclass
class MatchResult:
    matches: List[Match]
    path: Optional[List[Road]] = None
