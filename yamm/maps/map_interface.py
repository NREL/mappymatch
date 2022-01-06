from enum import Enum
from typing import List

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
    def nearest_road(
        self,
        coord: Coordinate,
    ) -> Road:
        """
        return the nearest road to a coordinate
        :param coord: the coordinate
        :return: the nearest road
        """

    @abstractmethod
    def shortest_path(
        self,
        origin: Coordinate,
        destination: Coordinate,
        weight: PathWeight = PathWeight.TIME,
    ) -> List[Road]:
        """
        computes the shortest path on the road network

        :param origin:
        :param destination:
        :param weight:

        :return:
        """
