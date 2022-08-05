Contributing
==================== 

.. contents:: Overview
   :depth: 2
   :local: 

Getting Started
----------------- 
We are happy your are even considering helping. We hope this guide makes the process seamless. We really appreciate your help! 

If you are new to open source contribution, please checkout :ref:`best-practices` and :ref:`toolbelt`. 

.. note:: 
   All command line code is run from the project root except where noted.

.. tip:: 
   In :code:`git clone <forked_repo_https_link.git>` , text inside the < >, and the < > get replaced with the appropriate specific text. The < > visually separate the syntax which remains unchanged from the text that needs to be changed. It is a common development pattern that is confusing if you have not seen it before. To see another example of it, type :code:`git --help` on your command line.

Select an issue 
----------------
Look through the open issues and for an issue labelled ``good first issue`` or ``documentation`` that is unassigned. 

Once you have selected an issue, then assign it to yourself by placing the word ``take`` as a comment. This will indicate to other contributors that you're working on the issue. Your goal is to finish the process from self assigning the issue to submitting the initial Pull Request (PR) in less than 2 weeks. This keeps your work from diverging too much from the main branch. 

That being said, life happens, we appreciate you however you decide to help. If something comes up, and you need to unassign an issue (place the word ``remove`` as a comment) or post that you are still working on it, then that is okay. 


Build from the source (First time only)
----------------------------------------------
   #. Go to the `repo <https://github.com/NREL/mappymatch>`_ and click on :guilabel:`Fork` in the upper right.
   #. Navigate to your fork which will be <you_user_name>/mappymatch . Click on the green :guilabel:`Code` drop down and copy the https link. 
   #. From the command line:  

      .. code-block:: sh 
         :caption: Clone the forked repo.

         git clone <forked_repo_https_link.git>

      .. code-block:: sh
         :caption: Create the Conda environment, and activate it. You will need to run each command separately.

         cd mappymatch
         conda env create -f environment_dev.yml
         conda activate mappymatch_dev

      .. code-block:: sh 
         :caption: Verify installation by running tests. 

         python -m unittest discover 

      .. code-block:: output
         :caption: Return should look like this, but the number of tests will vary. 

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

   #. 
      .. code-block:: 
         :caption: Checkout a branch from your forked repository 
   
         git checkout -b <descriptive_branch_name>

   #. Make your changes and add commits 

   #. Pull in changes from upstream. This is best done periodically, if you have the branch checked out for a long time.

      .. code-block:: 
         :caption: Switch to main branch, pull changes from upstream, resolve conflicts that arise. 
   
         git checkout main 
         git pull upstream main

      .. code-block:: 
         :caption: Switch to your branch, pull the changes from your main repository, and resolve conflicts that arise.
   
         git checkout <descriptive_branch_name>
         git pull origin main 

   #. Push changes to get ready for PR. 

      .. code-block:: 
         :caption: Push your changes to remote for your forked repository.

         git push origin <descriptive_branch_name>


Open a PR
---------------------------------------------

   #. Go to the `repo/PR <https://github.com/NREL/mappymatch/pulls>`_ and click on :guilabel:`New pull request` in the upper right.
   #. Click on :guilabel:`Compare across forks` in the top middle. 
   #. Leave the ``base repository`` section alone. For the ``head repository`` section select your fork and your branch. 
   #. **Review the code diffs** and then click :guilabel:`Create pull request`. 
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

.. _best-practices:

Best practices
---------------------------------------------
Asking questions 
_____________________________________________
Have a question? Rather than opening an issue, please ask questions
or post comments in `Q&A Discussions <https://github.com/NREL/mappymatch/discussions/categories/q-a>`_ .
Members of the community are happy to assist. 

Providing feedback 
______________________________________________
Your comments and feedback are very welcome. Please post to
`General Discussions <https://github.com/NREL/mappymatch/discussions/categories/general>`_ 
with lots of detail.

Reporting issues 
______________________________________________
We are happy to fix bugs. Please report buys using the issues template. 

General issue reporting guidelines 
______________________________________________

   * One issue per problem. 

   * Check through the closed issues before submitting a new one.  

Requesting features 
_______________________________________________
If you are interested in coding or requesting a new feature, let us know in
`Ideas Discussions <https://github.com/NREL/mappymatch/discussions/categories/ideas>`_ 
Please wait for confirmation from a core maintainer before proceeding.


Previewing documentation locally 
--------------------------------------------
To preview the documentation locally:

   #. From the command line, use `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to rebuild the docs.

      .. code-block:: sh 

         sphinx-autobuild -b html ./docs/source ./docs/_build 
   
   #. Open ``http://127.0.0.1:8000`` with your browser.

.. _toolbelt:

Maintainer Information 
---------------------------------------- 

Updating Version Locations 
________________________________________ 

To update the version automatically using tbump: 

.. code-block:: sh 

   tbump <version_major.version_minor.version_patch> --only-patch

To update the version manually update it in the following locations: 

   #. In the docs ``/docs/source/conf.py``
   #. In the setup.py ``/pyproject.toml``


Tools in our toolbelt
--------------------------------------- 
.. note:: 
   All command line examples use settings configured for the repo. Coverage and Isort automatically find their configuration files.

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

`Pre-Commit <https://pre-commit.com/>`_ is a framework for managing and maintaining multilanguage pre-commit hooks. Before the commit executes, pre-commit hooks are run to do useful things like code formatting. This means the unformatted code never enters your code base. 

Command line use: 

.. code-block:: sh 
   :caption: Run once to install hooks configured by .pre-commit-config.yaml

   pre-commit install 

.. code-block:: sh
   :caption: Make changes to the code base, add files to the staging area, and commit changes as you normally would.

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

