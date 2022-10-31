.. MapPyMatch documentation master file, created by
   sphinx-quickstart on Mon May  2 10:18:14 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _mainindex:

Mappymatch
========================

Mappymatch is a pure-python package developed and open sourced by the National Renewable Energy Laboratory. It contains a collection of "Matchers" that enable matching a GPS trace (series of GPS coordinates) to a map. 

The current and planned Matchers are:
---------------------------------------

   * ``LCSSMatcher`` A matcher that implements the LCSS algorithm described in this `paper <https://doi.org/10.3141%2F2645-08>`_. Works best with high resolution GPS traces.  


   * ``OsrmMatcher`` A light matcher that pings an OSRM server to request map matching results. See the `official documentation <http://project-osrm.org/>`_ for more info.

   * ``ValhallaMatcher (planned)`` A matcher to ping a `Valhalla <https://www.interline.io/valhalla/>`_ server for map matching results. 

Currently supported map formats are: 
--------------------------------------- 

   * ``Open Street Maps`` 

.. toctree::
   :maxdepth: 3
   :caption: Documentation Index:

   general/quickstart 
   general/install 
   general/examples 
   reference/index
   general/contributing
   general/changelog
   general/contributors
 
.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`