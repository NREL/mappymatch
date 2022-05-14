Contributing
==================== 

Contributing 
-----------------

Using Coverage (Not currently implement in CI) :

`Coverage <https://coverage.readthedocs.io/en/latest/>`_ is a tool used to monitor test coverage. It does so by excuting the tests and monitoring which lines are run. 

To use it from your command line: 

.. code-block:: sh 
   :caption: Run the tests with coverage monitoring.

   coverage -m unittest discover 

.. code-block:: sh
   :caption: View the coverage report.

   coverage report -m