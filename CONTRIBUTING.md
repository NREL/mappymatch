# Contributing to mappymatch 

We're excited that you're considering contributing to the mappymatch package!
There are a variety of ways in which you can contribute beyond writing code.
This document provides a high-level overview of how you can get involved.


## Asking Questions

Have a question? Rather than opening an issue directly, please ask questions
or post comments in [Q&A Discussions](https://github.com/NREL/mappymatch/discussions/categories/q-a).
The NREL team or other members of the community will assist. Your well-worded
question will serve as a resource to others searching for help.


## Providing Feedback

Your comments and feedback are very welcome. Please post to
[General Discussions](https://github.com/NREL/mappymatch/discussions/categories/general)
with lots of information and detail. It is beneficial to consider
how someone else will understand your comments in order to make
them most effective.


## Reporting Issues

Have you identified a reproducible problem in mappymatch?
Have a feature request? We want to hear about it! Here's how you can make
reporting your issue as effective as possible.

### Writing Good Bug Reports and Feature Requests

File a single issue per problem and feature request. Do not enumerate
multiple bugs or feature requests in the same issue.

Do not add your issue as a comment to an existing issue unless it's for the
identical input. Many issues look similar, but have different causes.

The more information you can provide, the more likely someone will
be successful at reproducing the issue and finding a fix.

Please follow the issue template guidelines to include relevant information
that will help in diagnosing the problem.

### Final Checklist

Please remember to do the following:

- [ ] Search the issue repository to ensure your report is a new issue

- [ ] Recreate the issue with a minimally descriptive example

- [ ] Simplify your code around the issue to better isolate the problem


## Contributing Fixes / Features

If you are interested in writing code to fix an issue or
submit a new feature, let us know in
[Ideas Discussions](https://github.com/NREL/mappymatch/discussions/categories/ideas)!

If you receive a confirmation from a core maintiner to proceed with your 
change or improvement:

#### 1. Fork the repository

#### 2. Clone the Repo Locally and Install Dependencies

```
git clone https://github.com/<your_github_username>/mappymatch.git
```

Change directory into the mappymatch folder:
```
cd path/to/mappymatch   # from here, your path to mappymatch is likely .\mappymatch\
```

Then, use the contributor_environment.yml file (which was downloaded when you 
cloned the repo) to install dependencies:
```
conda env create -f contributor_environment.yml
```

To activate the mappymatch environment:
```
conda activate mappymatch
```

In addition, `plot` is needed to plot the results in the examples.

This can be installed via pip:
```
pip install ".[plot]"
```

The final step before creating a new brach for development is to install
your pre-commit hooks:
```
pre-commit install
```


#### 3. Create a new branch for local development

Create a new branch and make the changes, updates, or improvements you desire.

How to create a new branch:

```
git checkout -b <name-of-your-bugfix-or-feature>
```

#### 4. Check Your Code

 Once you are finished making your changes, please thoroughly check your code.
 While we will eventually have automated checks that run before code is commited 
 via pre-commit and GitHub Actions to run tests before code can be merged, at this time
 you can use a formatter in your IDE such as `black` and a style guide enforcer such
 as `flake8` to reduce the chance of us rejecting your PR.

#### 5. Commit Your Changes

Now you can commit your changes and push your branch to GitHub
```
git add .
git commit -m "Your detailed description of your changes."
git push origin <name-of-your-bugfix-or-feature> # same name as the branch you created
```

#### 6. Submit a Pull Request Through the GitHub Website

Congrats! You've almost made it! You code is now ready to be reviewed by the 
maintainers. Go to your fork and create a pull request. Make sure you select
the correct branch on your fork to merge with the main branch of the original
repo.

#### 7. Fix any remaining issues

It's rare, but you might at this point still encounter issues, as the continuous 
integration (CI) system on GitHub Actions checks your code. Some of these might 
not be your fault; rather, it might well be the case that your code fell a little 
bit out of date as others' pull requests are merged into the repository.

In any case, if there are any issues, the pipeline will fail out. We check for 
code style, docstring coverage, test coverage, and doc discovery. If you're 
comfortable looking at the pipeline logs, feel free to do so; they are open to all 
to view. Otherwise, one of the dev team members can help you with reviewing the 
code checks.
