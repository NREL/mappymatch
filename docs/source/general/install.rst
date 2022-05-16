Install
================== 

From PyPI
^^^^^^^^^

TODO

From Source (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^

First, clone the repository::

   git clone https://github.com/NREL/mappymatch.git && cd mappymatch

Then, setup a python environment with Python (at least version 3.8)::

   conda create -n mappymatch python=3.8

Finally, use pip to install the package::

   pip install -e .

.. warning::

   If you have issues installing the package and dependencies, you can try swapping step two above with the following command::

      conda env create -f environment.yml