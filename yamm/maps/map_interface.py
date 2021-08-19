from enum import Enum
from typing import List, Optional

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.road import Road
from yamm.utils.abc import *


class PathWeight(Enum):
    DISTANCE = 0
    TIME = 0


class MapInterface(metaclass=ABCMeta):
    """
    abstract base class for a Matcher
    """

    @abstractattribute
    def roads(self) -> List[Road]:
        """
        get a list of all the roads in the map

        :return: a list of the roads in the map
        """

    @abstractmethod
    def coordinate_outside_boundary(self, coord: Coordinate, max_distance: float = 3000) -> bool:
        """
        test if there is a road within the max distance

        :param coord:
        :param max_distance:

        :return:
        """

    @abstractmethod
    def nearest_roads(
            self,
            coord: Coordinate,
            k: int = 1,
            search_size: float = 200,
            max_distance: float = 3000,
    ) -> List[Road]:
        """
        return the nearest road(s) to a coordinate
        :param coord:
        :param k:
        :param search_size:
        :param max_distance:
        :return:
        """

    @abstractmethod
    def shortest_path(self, origin: Coordinate, destination: Coordinate, weight: PathWeight = PathWeight.TIME) -> List[
        Road]:
        """
        computes the shortest path on the road network

        :param origin:
        :param destination:
        :param weight:

        :return:
        """
