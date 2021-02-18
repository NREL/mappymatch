from typing import List

from yamm.utils.abc import *
from yamm.utils.trace import Trace

# types
LinkId = str
MatchResult = List[LinkId]


class MatcherInterface(metaclass=ABCMeta):
    """
    abstract base class for a Matcher
    """

    @abstractmethod
    def match_trace(self, trace: Trace) -> MatchResult:
        """
        take in a trace of gps points and return a list of matching link ids

        :param trace: the trace to match

        :return: a list of matched link ids
        """

    @abstractmethod
    def match_trace_batch(self, trace_batch: List[Trace]) -> List[MatchResult]:
        """
        take in a batch of traces and return a batch of matching link ids

        :param trace_batch: the batch of traces to match

        :return: a list of match results
        """
