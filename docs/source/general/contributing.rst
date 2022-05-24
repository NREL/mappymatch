Contributing
==================== 

.. contents:: Overview
   :depth: 2
   :local: 

Getting Started
----------------- 
We are happy your are even considering helping. We hope this guide makes the process seamless. We really appreciate your help! 

If you are new to open source contribution, please checkout Tools in our toolchain and best practices sections. 


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

      .. code-block:: output
         :caption: Return should look something this, but test number may vary. 

         ................................................ 
         ---------------------------------------------------------------
         Ran 51 tests in 14.621s 

         OK


Install Pre-Commit hooks (First time only)
--------------------------------------------------------------------
.. code-block:: sh 
   
   pre-commit install


Setup Git workflow (First time only) 
--------------------------------------------------------------------
.. code-block:: sh 
   :caption: Setup upstream remote. 
   
   git remote add upstream https://github.com/NREL/mappymatch.git 


Execute Changes and Git workflow 
---------------------------------------------------------------
.. code-block:: 
   :caption: Checkout a branch from your forked repository 
   
   git checkout -b <descriptive_branch_name>

Make your changes and add commits 

Pull in changes from upstream. This is best done periodically, if you have the branch checked out for a long time.

.. code-block:: 
   :caption: Switch to main branch, pull changes from upstream, resolve conflicts that arise. 
   
   git checkout main 
   git pull upstream

.. code-block:: 
   :caption: Switch to your branch, pull the changes from your main repository, and resolve conflicts that arise.
   
   git checkout <descriptive_branch_name>
   git pull main 

Push changes to get ready for PR. 

.. code-block:: 
   :caption: Push your changes to remote for your forked repository.

   git push origin <descriptive_branch_name>


Open a PR
---------------------------------------------

   #. Go to the `repo/PR <https://github.com/NREL/mappymatch/pulls>`_ and click on ``New pull request`` in the upper right.
   #. Click on ``Compare across forks`` in the top middle. 
   #. Leave the ``base repository`` section alone. For the ``head repository`` select your fork and your branch. 
   #. Review the code diffs and then click ``Create pull request``. 
   #. Check back after a fewer minutes to make sure the CI steps pass. If they fail, then make the fixes and push your branch to your forked repo again. The PR will update and rerun the CI. 

Finish the PR 
--------------------------------------------- 

   #. Check back in a few days for maintainer requests for changes. Don't be surprised or offended by the changes. Most PRs require some changes.  
   #. Make the changes and push your branch to your forked repo again. 
   #. The maintainer will merge your branch. 
   #. Delete you branch 
   #. Pull the changes into your forked repo. 

      .. code-block:: sh

         git checkout main 
         git pull upstream main 


Best practices
---------------------------------------------
TBD

Tools in our toolbelt
--------------------------------------- 

.. note:: 
   All command line code is run from the project root except where noted and all command line example use the setting configured for the repo. 

.. tip:: 
   Coverage and Isort automatically find their configuration files.

Black 
__________________________________

Implemented as a Pre-Commit hook. 

`Black <https://github.com/psf/black>`_ is an opinionated code formatter so you don't have to be.  

Command line use: 

.. code-block:: sh 

   black --config pyproject.toml


Coverage 
___________________________________ 

Not Implemented as CI

`Coverage <https://coverage.readthedocs.io/en/latest/>`_ is a tool used to monitor test coverage. It does so by executing the tests and monitoring which lines are run. 

Command line use: 

.. code-block:: sh 
   :caption: Run the tests with coverage monitoring.

   coverage -m unittest discover 

.. code-block:: sh
   :caption: View the coverage report.

   coverage report -m 

Interrogate 
__________________________________
Implemented as Pre-Commit hook. 

`Interrogate <https://interrogate.readthedocs.io/en/latest/index.html>`_ reports on the level of and enforces docstring coverage for the code base. 

Command line use 

.. code-block:: sh 

   interrogate -c pyproject.toml


Isort 
__________________________________

Implemented as Pre-Commit hook. 

`Isort <https://pycqa.github.io/isort/>`_ automatically groups and sorts your import statements so you don't have to. 

Command line use: 

.. code-block:: sh 

   isort 

Pre-Commit
__________________________________

Implements all the precommit hooks.

`Pre-Commit <https://pre-commit.com/>`_ is a framework for managing and maintaining multilanguage pre-commit hooks. Before the commit executes and pre-commit hooks are run to do useful things like code formatting. This means the unformatted code never enters your code base. 

Command line use: 

.. code-block:: sh 
   :caption: Run once to install hooks as setup by .pre-commit-config.yaml

   pre-commit install 

.. code-block:: sh
   :caption: Make change to the code base, add files to the staging area, and commit changes as you normally would.

   git commit -m "Updated tools in toolchain docs section."

You will get a success or failure. 

.. code-block:: output
   :caption: Example output for success. No other steps are needed.

   black................................................(no files to check)Skipped
   isort (python).......................................(no files to check)Skipped
   interrogate..........................................(no files to check)Skipped
   [create_contributing_docs 30c2bf3] Updated tools in toolchain docs section.
   1 file changed, 80 insertions(+), 4 deletions(-)

.. code-block:: output
   :caption: Example output for failure. See next code block for follow on steps.

   black....................................................................Failed
   - hook id: black
   - files were modified by this hook

   reformatted mappymatch\utils\url.py

   All done! \u2728 \U0001f370 \u2728
   1 file reformatted.

   isort (python)...........................................................Passed
   interrogate..............................................................Passed
   

.. code-block:: sh 
   :caption: Re-add the files to the staging area. Commit again. You should get a success.

   git add --all 
   git commit -m "Update contributing docs for precommit-failure."
