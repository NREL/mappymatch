from os import path

from setuptools import setup, find_packages

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="yamm",
    version="0.2.0",
    description="yamm is a package for map matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.nrel.gov/MBAP/yamm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "networkx",
        "geopandas",
        "pygeos",
        "tqdm",
    ],
    extras_require={
        "osm": [
            "osmnx",
            "requests",
        ],
        "plot": [
            "folium",
        ],
    },
    include_package_data=True,
    package_data={
        "yamm.resources": ["*"],
    },
    author="National Renewable Energy Laboratory",
    license="Copyright ©2022 Alliance for Sustainable Energy, LLC All Rights Reserved",
)
