import logging as log

import osmnx as ox

ox.config(log_console=False)
log.basicConfig(level=log.INFO)


METERS_TO_KM = 1 / 1000
