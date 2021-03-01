# yamm
"yet another map matcher" is a library that maintains a collection of map matching algorithms and wrappers


# Examples

## OsrmMatcher

The OsrmMatcher communicates with an OSRM server to match a trace of points
(default is http://router.project-osrm.org but you can point to your own)

usage:
```python
from yamm.matchers.osrm import OsrmMatcher
from yamm.constructs.trace import Trace

matcher = OsrmMatcher()

trace = Trace.from_csv("path/to/trace.csv")

# only match first 5 points
links = matcher.match_trace(trace[:5])
```

yields:
```python
['(152978044,152993419)', '(152978044,152993419)', '(152978044,152993419)', '(152978044,152993419)', '(152978044,152993419)']
```


