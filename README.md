# yamm
"yet another map matcher" is a library that maintains a collection of map matching algorithms and wrappers

## Setup

### locally
Clone the repo, setup a python environment with python >= 3.8 and pip install the package

```
git clone https://github.nrel.gov/MBAP/yamm.git
conda create -n yamm python=3.9
cd yamm/
pip install -e .
```



## Examples

### OsrmMatcher

The OsrmMatcher communicates with an OSRM server to match a trace of points
(default is http://router.project-osrm.org but you can point to your own)

usage:
```python
from yamm.matchers.osrm import OsrmMatcher
from yamm.constructs.trace import Trace

matcher = OsrmMatcher()

trace = Trace.from_csv("resources/traces/sample_trace_1.csv")

# only match first 5 points
matches = matcher.match_trace(trace[:5])
```

### LCSSMatcher 

The LCSS Matcher implements the map matching algorithm described in this paper: 

Zhu, Lei, Jacob R. Holden, and Jeffrey D. Gonder.
"Trajectory Segmentation Map-Matching Approach for Large-Scale, High-Resolution GPS Data."
Transportation Research Record: Journal of the Transportation Research Board 2645 (2017): 67-75.

usage:
```python
from yamm.matchers.lcss.lcss import LCSSMatcher
from yamm.maps.tomtom_map import TomTomMap 
from yamm.constructs.trace import Trace

road_map = TomTomMap("resources/austin_tomtom_network.pickle")

matcher = LCSSMatcher(road_map)

trace = Trace.from_csv("resources/traces/sample_trace_1.csv")

matches = matcher.match_trace(trace)
```




