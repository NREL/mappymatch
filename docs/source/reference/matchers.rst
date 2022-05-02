Matchers
========

There are several matchers that can be used to determine the road that a coordinate is *matched* to. Matchers may have tradeoffs between speed and accuracy. Each map class must conform to the matcher interface defined in :class:`yamm.matchers.matcher_interface.MatcherInterface`.

Available Matchers
------------------

- :class:`yamm.matchers.line_snap.LineSnapMatcher`
- :class:`yamm.matchers.osrm.OsrmMatcher`

.. autoclass:: yamm.matchers.line_snap.LineSnapMatcher
    :members:

.. autoclass:: yamm.matchers.osrm.OsrmMatcher
    :members:

Matcher Interface
-----------------

.. automodule:: yamm.matchers.matcher_interface
    :members: