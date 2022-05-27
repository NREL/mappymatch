# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import date
from platform import release

sys.path.insert(0, os.path.abspath("../.."))
print(os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "Mappymatch"
year = date.today().year
copyright = f"{year}, National Renewable Energy Laboratory"
author = "National Renewable Energy Laboratory"
# Initial releases at 0.x.x
# First stable release at 1.x.x
version = "0.0.0"
release = "0.0.0-alpha"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
    "style_external_links": True,
    "style_nav_header_background": "#9B59B6",
}
# TODO https://www.sphinx-doc.org/en/master/usage/configuration.html?highlight=html_icon#confval-html_favicon
# html_logo = ''
# html_favicon = ''

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
# TODO Revised based on discussion #120.
add_module_names = True

# -- Post process ------------------------------------------------------------
import collections


def remove_namedtuple_attrib_docstring(app, what, name, obj, skip, options):
    if type(obj) is collections._tuplegetter:
        return True
    return skip


def setup(app):
    app.connect("autodoc-skip-member", remove_namedtuple_attrib_docstring)
