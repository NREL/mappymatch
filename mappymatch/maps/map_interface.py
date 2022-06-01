from __future__ import annotations

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.road import Road


class PathWeight(Enum):
    """
    An enum representing the weight of a path
    """

    DISTANCE = 0
    TIME = 0


class MapInterface(metaclass=ABCMeta):
    """
    Abstract base class for a Matcher
    """

    @property
    @abstractmethod
    def roads(self) -> List[Road]:
        """
        Get a list of all the roads in the map

        Returns:
            A list of all the roads in the map
        """

    @abstractmethod
    def nearest_road(
        self,
        coord: Coordinate,
    ) -> Road:
        """
        Return the nearest road to a coordinate

        Args:
            coord: The coordinate to find the nearest road to

        Returns:
            The nearest road to the coordinate
        """

    @abstractmethod
    def shortest_path(
        self,
        origin: Coordinate,
        destination: Coordinate,
        weight: PathWeight = PathWeight.TIME,
    ) -> List[Road]:
        """
        Computes the shortest path on the road network

        Args:
            origin: The origin coordinate
            destination: The destination coordinate
            weight: The weight to use for the path

        Returns:
            A list of roads that form the shortest path
        """
