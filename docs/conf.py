# encoding: utf-8

"""pyspotify documentation build configuration file"""

from __future__ import unicode_literals

import os
import re
import sys
import types

try:
    # Python 3.3+
    from unittest import mock
except ImportError:
    # Python <3.3
    import mock


def get_version(filename):
    init_py = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']


# -- Workarounds to have autodoc generate API docs ----------------------------

sys.path.insert(0, os.path.abspath('..'))


# Mock cffi module and cffi objects
cffi = mock.Mock()
cffi.__version__ = '0.8.1'
sys.modules['cffi'] = cffi
ffi = cffi.FFI.return_value
ffi.CData = bytes
lib = ffi.verify.return_value
lib.sp_error_message.return_value = b''
lib.sp_error_message.__name__ = str('sp_error_message')


# Add all libspotify constants to the lib mock
with open('sp-constants.csv') as fh:
    for line in fh.readlines():
        key, value = line.split(',', 1)
        setattr(lib, key, value)


# Unwrap decorated methods so Sphinx can inspect their signatures
import spotify  # flake8: noqa
for mod_name, mod in vars(spotify).items():
    if not isinstance(mod, types.ModuleType) or mod_name in ('threading',):
        continue
    for class_name, cls in vars(mod).items():
        if not isinstance(cls, type):
            continue
        for method_name, method in vars(cls).items():
            if hasattr(method, '__wrapped__'):
                setattr(cls, method_name, method.__wrapped__)


# -- General configuration ----------------------------------------------------

needs_sphinx = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'pyspotify'
copyright = '2013-2015, Stein Magnus Jodal and contributors'

release = get_version('../spotify/__init__.py')
version = '.'.join(release.split('.')[:2])

exclude_patterns = ['_build']

pygments_style = 'sphinx'

modindex_common_prefix = ['spotify.']

autodoc_default_flags = ['members', 'undoc-members', 'inherited-members']
autodoc_member_order = 'bysource'

intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
    'pyalsaaudio': ('http://pyalsaaudio.sourceforge.net', None),
}


# -- Options for HTML output --------------------------------------------------

html_theme = 'default'
html_static_path = ['_static']

html_use_modindex = True
html_use_index = True
html_split_index = False
html_show_sourcelink = True

htmlhelp_basename = 'pyspotify'

# -- Options for extlink extension --------------------------------------------

extlinks = {
    'issue': ('https://github.com/mopidy/pyspotify/issues/%s', '#'),
}
