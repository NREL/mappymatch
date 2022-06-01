Matchers
========

There are several matchers that can be used to determine the road that a coordinate is *matched* to. 
Matchers may have tradeoffs between speed and accuracy. 
Each Matcher class must conform to the matcher interface defined in :class:`mappymatch.matchers.matcher_interface.MatcherInterface`.

Available Matchers
------------------

- :class:`mappymatch.matchers.lcss.lcss.LCSSMatcher`
- :class:`mappymatch.matchers.line_snap.LineSnapMatcher`
- :class:`mappymatch.matchers.osrm.OsrmMatcher`

.. autoclass:: mappymatch.matchers.lcss.lcss.LCSSMatcher
    :members:

.. autoclass:: mappymatch.matchers.line_snap.LineSnapMatcher
    :members:

.. autoclass:: mappymatch.matchers.osrm.OsrmMatcher
    :members:
