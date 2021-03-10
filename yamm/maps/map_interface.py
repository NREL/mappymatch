from typing import List, Optional

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.road import Road
from yamm.utils.abc import *

Path = List[Road]


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
    def shortest_path(self, origin: Coordinate, destination: Coordinate, weight: Optional[str] = None) -> Path:
        """
        computes the shortest path on the road network

        :param origin:
        :param destination:
        :param weight:

        :return:
        """
