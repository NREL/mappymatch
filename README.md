# mappymatch
mappymatch is a pure-python package developed by the National Renewable Energy Laboratory that maintains a collection of map matching algorithms and wrappers. The package was designed for ease of use and portabilty across platforms.

## Setup

### Standard Method

Clone the repo:
```
git clone https://github.com/NREL/mappymatch.git
```

Change directory into the mappymatch folder:
```
cd path/to/mappymatch
# from here, your path to mappymatch is likely .\mappymatch\
```

Then, use the environment.yml file (which was downloaded when you cloned the repo) to install dependencies:

---> Question about this ordering (for @nreinicke or admin).
Should this instalation be performed before or after navigating into the subfolder mappymatch/mappymatch?
The environment.yml file lives in the outer directory under the primary MappyMatch folder.




```
conda env create -f environment.yml

# Is there a reason we are not using the line below? It allows us to specify the name and the filename in one line.
# conda env create -n mappymatch --file environment.yml
```

To activate the mappymatch environment:
```
conda activate mappymatch

```

Finally, be sure to change your Python interpreter path to the ./mappymatch/bin/python interpreter

There are a couple of extras available:

* `plot`: Needed to plot the result.

At least `plot` is needed to run the examples.

This can be installed via pip:
```
pip install ".[plot]"
```
The last step is to install the pre-commit hooks.
```
pre-commit install
```
## Example Usage

The current primary workflow is to use [osmnx](https://github.com/gboeing/osmnx) to download a road network and match it using the `LCSSMatcher`.

The `LCSSMatcher` implements the map matching algorithm described in this paper:

[Zhu, Lei, Jacob R. Holden, and Jeffrey D. Gonder.
"Trajectory Segmentation Map-Matching Approach for Large-Scale, High-Resolution GPS Data."
Transportation Research Record: Journal of the Transportation Research Board 2645 (2017): 67-75.](https://doi.org/10.3141%2F2645-08)

usage:
```python
from mappymatch import root
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.geo import geofence_from_trace
from mappymatch.maps.nx.readers.osm_readers import read_osm_nxmap
from mappymatch.constructs.trace import Trace

trace = Trace.from_csv(root() / "resources/traces/sample_trace_1.csv")

# generate a geofence polygon that surrounds the trace; units are in meters;
# this is used to query OSM for a small map that we can match to
geofence = geofence_from_trace(trace, padding=1e3)

# uses osmnx to pull a networkx map from the OSM database
road_map = read_osm_nxmap(geofence)

matcher = LCSSMatcher(road_map)

matches = matcher.match_trace(trace)
```
