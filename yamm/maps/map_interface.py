from typing import List

from yamm.constructs.road import Road
from yamm.utils.abc import *


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
