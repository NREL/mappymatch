# mappymatch
mappymatch is a pure-python package developed by the National Renewable Energy Laboratory that maintains a collection of map matching algorithms and wrappers. The package was designed for ease of use and portabilty across platforms.

## Setup

### Prerequisites

#### Windows

The Geospatial Data Abstraction Library (GDAL) does not play very nicely with Windows and Pip. The recommended solution
is to install gdal using conda

```
conda install gdal
```

If conda is not an option, there are two possible solutions.

##### 1) Install GDAL from source
This is the most difficult solution, but is trusted.


Before installing the required dependencies, install GDAL into the system. This process is documented
by [UCLA](https://web.archive.org/web/20220317032000/https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows).

##### 2) Install GDAL from binary wheel
This is the easiest solution, but it is from an untrusted source and is not to be used in sensitive environments.

| :exclamation:  Unofficial Vendor!|
|------------------------------------------|

A precompiled binary wheel is provided by Christoph Gohlke of the Laboratory for Fluorescence Dynamics at the 
University of California. If you use this approach, both GDAL and Fiona wheels need to be installed.

GDAL wheels: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
Fiona wheels: https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona 

1. Download the correct GDAL and Fiona wheels for your architecture and Python version
2. Create the virtual environment: `conda create -n yamm python=3.8`
3. Install the GDAL wheel into the virtual environment `pip install <path_to_GDAL_whl>`
4. Install the Fiona wheel into the virtual environment `pip install <path_to_Fiona_whl>`
5. Use pip to install the remaining packages `pip install -e <path/to/yamm>`

### Standard Setup

Clone the repo:

```
git clone https://github.com/NREL/mappymatch.git
```

Then, setup a python environment with python >= 3.8:

```
conda create -n mappymatch python=3.8
```

Finally, use pip to install the package:

```
conda activate mappymatch
pip install -e <path/to/mappymatch> 
```

### Alternate Setup

There are a couple of extras available:

* `osrm`: Needed by the `OsrmMatcher` to connect to the OSRM API.
* `plot`: Needed to plot the result.

At least `plot` is needed to run the examples.


If you have issues installing the package and dependencies using pip you can try using conda to install the
dependencies:

Clone the repo:

```
git clone https://github.com/NREL/mappymatch.git
```

Then, use the provided environment.yml file to install dependencies:

```
conda env create -f environment.yml
```

Finally, use pip to install the package:

```
conda activate mappymatch
pip install -e <path/to/mappymatch> 
```

## Example Usage

The current primary workflow is to use [osmnx](https://github.com/gboeing/osmnx) to download a road network and match it
using the `LCSSMatcher`.

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
