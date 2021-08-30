"""isort:skip_file"""
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
from importlib import import_module
from inspect import getsourcefile, getsourcelines
from pathlib import Path
from shutil import copy

sys.path.insert(0, os.path.abspath(".."))
import mad_gui

# -- Copy README file --------------------------------------------------------
copy(Path("../README.md"), Path("./README.md"))

# -- Project information -----------------------------------------------------

project = "MaD GUI Userguide"
copyright = "2021, Malte Ollenschlaeger, Arne Kuederle, Ann-Kristin Seifer"
author = "Malte Ollenschlaeger, Arne Kuederle, Ann-Kristin Seifer"
URL = "https://github.com/mad-lab-fau/mad-gui/blob/main"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    # "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "numpydoc",
    "sphinx.ext.linkcode",
    "sphinx.ext.intersphinx",
    "recommonmark",
    "sphinx_markdown_tables",
]
autodoc_mock_imports = ["PySide2"]
autodoc_default_options = {
    "members": True,
    "inherited-members": False,
    "imported-members": False,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["templates"]
autosummary_generate = True
autosummary_generate_overwrite = True
numpydoc_show_class_members = True
numpydoc_show_inherited_class_members = False
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "templates"]

# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
numpydoc_class_members_toctree = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_logo = "_static/images/logo_mad_man.png"
html_favicon = "_static/images/mad-runner.ico"
html_static_path = ['_static']
html_css_files = ['css/custom.css']
html_theme_options = {"show_prev_next": False}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# intersphinx configuration
intersphinx_module_mapping = {
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/{.major}".format(sys.version_info), None),
    **intersphinx_module_mapping,
}
# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


def get_nested_attr(obj, attr):
    attrs = attr.split(".", 1)
    new_obj = getattr(obj, attrs[0])
    if len(attrs) == 1:
        return new_obj
    else:
        return get_nested_attr(new_obj, attrs[1])


def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    if not info["module"]:
        return None
    module = import_module(info["module"])
    obj = get_nested_attr(module, info["fullname"])
    code_line = None
    filename = ""
    try:
        filename = str(
            Path(getsourcefile(obj)).relative_to(
                Path(getsourcefile(mad_gui)).parent.parent
            )
        )
    except:
        pass
    try:
        code_line = getsourcelines(obj)[-1]
    except:
        pass
    if filename:
        if code_line:
            return "{}/{}#L{}".format(URL, filename, code_line)
        return "{}/{}".format(URL, filename)


def skip_properties(app, what, name, obj, skip, options):
    """This removes all properties from the documentation as they are expected to be documented in the docstring."""
    if isinstance(obj, property):
        return True


def setup(app):
    app.connect("autodoc-skip-member", skip_properties)
