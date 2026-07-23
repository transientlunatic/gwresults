"""Sphinx configuration for gwresults."""

from importlib.metadata import version as _version

project = "gwresults"
copyright = "2026, Daniel Williams"
author = "Daniel Williams"

try:
    release = _version("gwresults")
except Exception:  # pragma: no cover
    release = "0.0.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx_click",
]

autosummary_generate = True
numpydoc_show_class_members = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "astropy": ("https://docs.astropy.org/en/stable", None),
}

html_theme = "furo"
html_static_path = ["_static"]
