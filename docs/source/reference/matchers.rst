Matchers
========

There are several matchers that can be used to determine the road that a coordinate is *matched* to. Matchers may have tradeoffs between speed and accuracy. 

Available Matchers
------------------ 

For readability, the full path is listed below and not used in other parts of the documentation.

- :class:`mappymatch.matchers.lcss.lcss.LCSSMatcher`
- :class:`mappymatch.matchers.line_snap.LineSnapMatcher`
- :class:`mappymatch.matchers.valhalla.ValhallaMatcher`
- :class:`mappymatch.matchers.osrm.OsrmMatcher`

LCSS 
----------
.. autoclass:: mappymatch.matchers.lcss.lcss.LCSSMatcher
    :members:

Line Snap 
-------------
.. autoclass:: mappymatch.matchers.line_snap.LineSnapMatcher
    :members:

Valhalla
--------------
.. autoclass:: mappymatch.matchers.valhalla.ValhallaMatcher
    :members: 

Osrm
--------------
.. autoclass:: mappymatch.matchers.osrm.OsrmMatcher 
    :members: 

Matcher Inferface 
-------------------- 

Each Matcher class must conform to the matcher interface defined below.

.. autoclass:: mappymatch.matchers.matcher_interface.MatcherInterface
    :members: