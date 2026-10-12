"""Unified Sphinx documentation for FoodFlow seminars 01–06."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
project = 'FoodFlow · Төслийн баримтжуулалт'
author = 'Ю. Төгөлдөр · 23B1NUM2350'
release = '0.6.2'
extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.napoleon',
              'sphinx.ext.doctest', 'sphinxcontrib.mermaid']
source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}
root_doc = 'index'
exclude_patterns = ['.codex-tools/**', 'archive/**', 'source_notes/**', 'public/**',
                    'build/**', 'node_modules/**', '.git/**', '.github/**',
                    'reports/assets/**', 'sources/student/**', '.gitlab/**',
                    'Week_06_FoodFlow_Improved.md',
                    'docs/source/index.rst', 'docs/source/verification.rst']
autodoc_typehints = 'description'
myst_heading_anchors = 4
myst_fence_as_directive = ['mermaid']
myst_enable_extensions = ['colon_fence']
html_theme = 'alabaster'
html_static_path = ['source/_static']
html_css_files = ['foodflow.css']
html_extra_path = ['api/openapi.yaml', 'api/swagger.html', 'api/redoc.html']
html_theme_options = {'description': 'Audience → Requirements → Architecture → API → Verification',
                      'fixed_sidebar': True, 'page_width': '1180px', 'sidebar_width': '260px'}
html_title = 'FoodFlow — Програм хангамжийн төслийн баримтжуулалт'
html_show_sourcelink = True
html_sidebars = {'**': ['about.html', 'navigation.html', 'searchfield.html']}
