Install
================== 

From Source (recommended) 
-------------------------
Clone the repo::

   git clone https://github.com/NREL/mappymatch.git && cd mappymatch

Then, use the environment.yml file (in the repo) to install dependencies::

   conda env create -f environment.yml

To activate the mappymatch environment::

   conda activate mappymatch

From PyPI
---------

.. code-block::

  pip install mappymatch 

.. warning::

   Some users have reported problems installing GDAL (a dependency of geopandas) on windows.
   Here are two possible solutions: 
   
   1) Install GDAL from source
   This is the most difficult solution, but is trusted.

   Before installing the required dependencies, install GDAL into the system. This process is documented
   by `UCLA <https://web.archive.org/web/20220317032000/https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows>`_.

   2) Install GDAL from binary wheel
   This is the easiest solution, but it is from an untrusted source and is not to be used in sensitive environments.

   A precompiled binary wheel is provided by Christoph Gohlke of the Laboratory for Fluorescence Dynamics at the 
   University of California. If you use this approach, both GDAL and Fiona wheels need to be installed.

   * `GDAL wheels <https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal>`_
   * `Fiona wheels <https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona>`_

   #. Download the correct GDAL and Fiona wheels for your architecture and Python version
   #. Install the GDAL wheel into the virtual environment `pip install <path_to_GDAL_whl>`
   #. Install the Fiona wheel into the virtual environment `pip install <path_to_Fiona_whl>`
   #. Use pip to install the remaining packages `pip install <path/to/mappymatch>`


From Conda
----------

|:construction:| We're currently working on a Conda package for mappymatch.