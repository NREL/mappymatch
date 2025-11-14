from abc import ABCMeta, abstractmethod

from mappymatch.constructs.trace import Trace
from mappymatch.matchers.match_result import MatchResult


class MatcherInterface(metaclass=ABCMeta):
    """
    Abstract base class for a Matcher
    """

    @abstractmethod
    def match_trace(self, trace: Trace) -> MatchResult:
        """
        Take in a trace of gps points and return a list of matching link ids

        Args:
            trace: The trace to match

        Returns:
            A list of Match objects
        """
