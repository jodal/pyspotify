# encoding: utf-8

"""pyspotify documentation build configuration file"""

from __future__ import unicode_literals

import os
import sys


# -- Workarounds to have autodoc generate API docs ----------------------------

sys.path.insert(0, os.path.abspath('..'))


# -- General configuration ----------------------------------------------------

needs_sphinx = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'pyspotify'
copyright = u'2013, Stein Magnus Jodal and contributors'

release = '2.0.0a1.dev0'
version = '.'.join(release.split('.')[:2])

exclude_patterns = ['_build']

pygments_style = 'sphinx'

modindex_common_prefix = ['spotify.']

autodoc_default_flags = ['members', 'undoc-members', 'inherited-members']
autodoc_member_order = 'bysource'


# -- Options for HTML output --------------------------------------------------

html_theme = 'default'
html_static_path = ['_static']

html_use_modindex = True
html_use_index = True
html_split_index = False
html_show_sourcelink = True

htmlhelp_basename = 'pyspotify'
