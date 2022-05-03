Matchers
========

There are several matchers that can be used to determine the road that a coordinate is *matched* to. Matchers may have tradeoffs between speed and accuracy. Each map class must conform to the matcher interface defined in :class:`mappymatch.matchers.matcher_interface.MatcherInterface`.

Available Matchers
------------------

- :class:`mappymatch.matchers.line_snap.LineSnapMatcher`
- :class:`mappymatch.matchers.osrm.OsrmMatcher`

.. autoclass:: mappymatch.matchers.line_snap.LineSnapMatcher
    :members:

.. autoclass:: mappymatch.matchers.osrm.OsrmMatcher
    :members:

Matcher Interface
-----------------

.. automodule:: mappymatch.matchers.matcher_interface
    :members: