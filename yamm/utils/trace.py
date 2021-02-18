from __future__ import annotations

from csv import DictReader
from pathlib import Path
from typing import List

from yamm.utils.geo import Coordinate


class Trace:
    def __init__(self, coords: List[Coordinate]):
        self.coords = coords

    def __getitem__(self, i):
        return Trace(self.coords[i])

    @classmethod
    def from_csv(cls, file: str) -> Trace:
        filepath = Path(file)
        if not filepath.is_file():
            raise FileNotFoundError(file)
        elif not filepath.suffix == ".csv":
            raise TypeError(f"file of type {filepath.suffix} does not appear to be a csv file")

        coords = []
        with filepath.open('r') as f:
            reader = DictReader(f)

            for row in reader:
                coords.append(Coordinate.from_dict(row))

        return Trace(coords)
