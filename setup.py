from os import path

from setuptools import setup, find_packages

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mappymatch",
    version="0.2.1",
    description="mappymatch is a package for map matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NREL/mappymatch",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    packages=find_packages(),
    python_requires=">=3.8", #! should we update this in the environment.yml file?
    install_requires=[
        "osmnx",
        "pygeos",
    ],
    extras_require={
        "osrm": [
            "requests",
        ],
        "plot": [
            "folium",
        ],
    },
    include_package_data=True,
    package_data={
        "mappymatch.resources": ["*"],
    },
    author="National Renewable Energy Laboratory",
    license="Copyright ©2022 Alliance for Sustainable Energy, LLC All Rights Reserved",
)
