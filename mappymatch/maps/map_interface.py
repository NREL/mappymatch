from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable, List, Optional, Union

from mappymatch.constructs.coordinate import Coordinate
from mappymatch.constructs.road import Road, RoadId

DEFAULT_DISTANCE_WEIGHT = "kilometers"
DEFAULT_TIME_WEIGHT = "minutes"


class MapInterface(metaclass=ABCMeta):
    """
    Abstract base class for a Matcher
    """

    @property
    @abstractmethod
    def distance_weight(self) -> str:
        """
        Get the distance weight

        Returns:
            The distance weight
        """
        return DEFAULT_DISTANCE_WEIGHT

    @property
    @abstractmethod
    def time_weight(self) -> str:
        """
        Get the time weight

        Returns:
            The time weight
        """
        return DEFAULT_TIME_WEIGHT

    @property
    @abstractmethod
    def roads(self) -> List[Road]:
        """
        Get a list of all the roads in the map

        Returns:
            A list of all the roads in the map
        """

    @abstractmethod
    def road_by_id(self, road_id: RoadId) -> Optional[Road]:
        """
        Get a road by its id

        Args:
            road_id: The id of the road to get

        Returns:
            The road with the given id or None if it does not exist
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
        weight: Optional[Union[str, Callable]] = None,
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
