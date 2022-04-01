# yamm
"yet another map matcher" is a pure-python package developed by the National Renewable Energy Laboratory that maintains a collection of map matching algorithms and wrappers. The package was designed for ease of use and portabilty across platforms.

## Setup

### Standard Method

Clone the repo:
```
git clone https://github.nrel.gov/MBAP/yamm.git
```

Then, setup a python environment with python >= 3.8:
```
conda create -n yamm python=3.8
```

Finally, use pip to install the package:
```
pip install -e <path/to/yamm> 
```

### Alternate Methods

If you have issues installing the package and dependencies using pip you can try using conda to
install the dependencies:

Clone the repo:
```
git clone https://github.nrel.gov/MBAP/yamm.git
```

Then, use the provided environment.yml file to install dependencies:
```
conda env create -f environment.yml
```

Finally, use pip to install the package:
```
pip install -e <path/to/yamm> 
```


## Example Usage

The current primary workflow is to use [osmnx](https://github.com/gboeing/osmnx) to download a road network and match it using the `LCSSMatcher`.

The `LCSSMatcher` implements the map matching algorithm described in this paper: 

[Zhu, Lei, Jacob R. Holden, and Jeffrey D. Gonder.
"Trajectory Segmentation Map-Matching Approach for Large-Scale, High-Resolution GPS Data."
Transportation Research Record: Journal of the Transportation Research Board 2645 (2017): 67-75.](https://doi.org/10.3141%2F2645-08)

usage:
```python
from yamm import root
from yamm.matchers.lcss.lcss import LCSSMatcher
from yamm.utils.geo import geofence_from_trace
from yamm.maps.nx.readers.osm_readers import read_osm_nxmap
from yamm.constructs.trace import Trace

trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")

# generate a geofence polygon that surrounds the trace; units are in meters;
# this is used to query OSM for a small map that we can match to
geofence = geofence_from_trace(trace, padding=1e3)

# uses osmnx to pull a networkx map from the OSM database
road_map = read_osm_nxmap(geofence)

matcher = LCSSMatcher(road_map)

matches = matcher.match_trace(trace)
```




