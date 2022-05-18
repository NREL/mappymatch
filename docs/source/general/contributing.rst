Contributing
==================== 

.. contents:: Overview
   :depth: 2
   :local: 

Getting Started
----------------- 
We are happy your are even considering helping. We hope this guide makes the process seamless. We really appreciate your help! 


Overview: 

   #. Pull a branch from your fork of mappymatch 
   #. Setup git precommit hooks (First time only)
   #. Review best practices (First time only)
   #. Read the overview for each tool in our precommit tool chain (First time only) 
   #. Review Git forking workflow (First time only)
   #. Make your changes and commit your changes 
   #. Complete your Git workflow to open your Pull Review (PR)
   #. Repository maintainer reviews your changes and recommends changes. 
   #. Make the recommended changes. 
   #. Complete your Git workflow to push the changes to you PR 
   #. Repository maintained accepts changes and merges PR. 
   #. Repeat

 

Select an issue 
----------------
Look through the open issues and for an issue labelled ``good first issue`` or ``documentation`` that currently unassigned. 

# TODO make github action for take and remove

Once you have selected an issue, then assign it to yourself by placing the word ``take`` as a comment. This will initiate a github action to assign it to you. It may take a few seconds or require you to refresh the page. Your goal is to finish the process from self assigning the issue to submitting initial Pull Request (PR) in less than 2 weeks. This keeps your work from diverging too much from the main branch. 

That being said, life happens, we appreciate you however you decide to help. If something comes up, and you need to unassign an issue (place the word ``remove`` as a comment) or post in the issue that you are still working on something, then that is okay. 


Build from the source (First time only)
----------------------------------------------
   #. On the github site, go to the `repo <https://github.com/NREL/mappymatch>`_ and click on ``Fork`` in the upper right.
   #. Navigate to your fork which will be <you_user_name>/mappymatch . Click on the green ``Code`` drop down and copy the https link. 
   #. From the command line:  

      .. code-block:: sh 
         :caption: Clone the forked repo.

         git clone <forked_repo_https_link.git>

      .. code-block:: sh
         :caption: Create the Conda environment, and activate it. You will need to run each command separately.

         cd mappy_match
         conda create -f contributor_environment.yml
         conda activate mappy_match 

      .. code-block:: sh 
         :caption: Verify install by running tests. 

         python -m unittest discover 

      .. code-block:: sh 
         :caption: Return should look something this, but test number may vary. 

         ................................................ 
         ---------------------------------------------------------------
         Ran 51 tests in 14.621s 

         OK


Setup upstream remote (First time only) 
--------------------------------------------------------------------








Using Coverage (Not currently implement in CI) :

`Coverage <https://coverage.readthedocs.io/en/latest/>`_ is a tool used to monitor test coverage. It does so by excuting the tests and monitoring which lines are run. 

To use it from your command line: 

.. code-block:: sh 
   :caption: Run the tests with coverage monitoring.

   coverage -m unittest discover 

.. code-block:: sh
   :caption: View the coverage report.

   coverage report -m