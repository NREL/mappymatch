from os import path

from setuptools import setup, find_packages

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="yamm",
    version="0.1.0",
    description=
    "yamm is a package for map matching",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.nrel.gov/MBAP/yamm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering"
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "networkx",
        "scipy",
        "pyproj",
        "shapely",
        "sqlalchemy",
        "geopandas",
    ],
    extras_require={
        "optional": [
            "osmnx",
            "requests",
            "rtree",
            "psycopg2",
        ],
        "plot": [
            "folium",
        ]
    },
    include_package_data=True,
    package_data={
        "yamm.resources": ["*"],
    },
    entry_points={
        'console_scripts': [
            'get-tomtom-network=scripts.get_tomtom_road_network:get_tomtom_network',
            'get-osm-network=scripts.get_osm_road_network:get_osm_network',
        ]
    },
    author="National Renewable Energy Laboratory",
    license="Copyright ©2020 Alliance for Sustainable Energy, LLC All Rights Reserved",
)
