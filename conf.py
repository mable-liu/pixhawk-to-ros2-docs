# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = "Raspberry Pi and Pixhawk Setup"
author = "Mable Liu"
copyright = "2026, Mable Liu"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
]

exclude_patterns = [
    "_build",
    ".venv",
    "Thumbs.db",
    ".DS_Store",
    "URA.md",
]

# -- MyST configuration ------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",      # ::: fenced directives, easier to read than ```{note}
    "deflist",          # definition lists for parameter/pin tables
    "linkify",          # bare URLs become links
    "substitution",     # reusable values (PX4 version, baud rates)
]

# Auto-generate anchors for headings so cross-page links to ## sections work.
myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
}
