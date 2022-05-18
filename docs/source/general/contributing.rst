Contributing
==================== 

.. contents:: Overview

Getting Started
----------------- 
We are always happy to have help. Follow this guide to get started. We really appreciate your help! 



Overview: 

   #. :ref:`select-an-issue`
   #. Build from the source (First time only)
   #. Setup upstream remote and Git workflow items (First time only) 
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


.. _select-an-issue: 

Select an issue 
----------------
It's best to go through the open issues and look for an issue that is labelled ``good first issue`` or an issue that has to do with documentation. 

# TODO make github action for take and remove

Once you have selected an issue, then assign it to yourself by placing the word ``take`` as a comment. This will initiate a github action to assign it to you. You goal is to finish the process from self assigning the issue to merging the pull review in less than 2 weeks. This keeps your work from diverging to much from the main branch. 

That being said, life happens, we appreciate however you decide to help. If something comes up and you need to unassign an issue (place the word ``remove`` as a comment) or post in the issue that you are still working on something, then that is okay. 


Build from the source 
--------------------------
   #. On the github site, go to the `repo <https://github.com/NREL/mappymatch>`_ and click on ``Fork`` in the upper right.
   #. Navigate to your fork which will be <you_user_name>/mappymatch . Click on the green ``Code`` drop down and copy the https link. 
   #. From the command line:  

      .. code-block:: sh 
         :caption: Clone the forked repo.

         git clone <forked_repo_https_link.git>

      .. code-block:: sh
         :caption: Create the Conda environment, activate it, and install dependencies. You will need to run each command separately.

         conda create --name mappy_match python=3.8
         conda activate mappy_match
         cd mappy_match 
         conda install -f contributor_environment.yml 



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