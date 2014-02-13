# encoding: utf-8

"""pyspotify documentation build configuration file"""

from __future__ import unicode_literals

import mock
import os
import re
import sys


def get_version(filename):
    init_py = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']


# -- Workarounds to have autodoc generate API docs ----------------------------

sys.path.insert(0, os.path.abspath('..'))


cffi = mock.Mock()
cffi.__version__ = '0.8.1'
ffi = cffi.FFI.return_value
ffi.CData = bytes
lib = ffi.verify.return_value
lib.sp_error_message.return_value = ''
lib.sp_error_message.__name__ = b'sp_error_message'

with open('sp-constants.csv') as fh:
    for line in fh.readlines():
        key, value = line.split(',', 1)
        setattr(lib, key, value)

sys.modules['cffi'] = cffi


# -- General configuration ----------------------------------------------------

needs_sphinx = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'pyspotify'
copyright = '2013-2014, Stein Magnus Jodal and contributors'

release = get_version('../spotify/__init__.py')
version = '.'.join(release.split('.')[:2])

exclude_patterns = ['_build']

pygments_style = 'sphinx'

modindex_common_prefix = ['spotify.']

autodoc_default_flags = ['members', 'undoc-members', 'inherited-members']
autodoc_member_order = 'bysource'

intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
}


# -- Options for HTML output --------------------------------------------------

html_theme = 'default'
html_static_path = ['_static']

html_use_modindex = True
html_use_index = True
html_split_index = False
html_show_sourcelink = True

htmlhelp_basename = 'pyspotify'
