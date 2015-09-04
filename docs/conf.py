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


# Mock cffi module
module = mock.Mock()
module.ffi = mock.Mock()
module.ffi.CData = bytes
module.lib = mock.Mock()
module.lib.sp_error_message.return_value = b''
module.lib.sp_error_message.__name__ = str('sp_error_message')
sys.modules['spotify._spotify'] = module


# Add all libspotify constants to the lib mock
with open('sp-constants.csv') as fh:
    for line in fh.readlines():
        key, value = line.split(',', 1)
        setattr(module.lib, key, value)


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
    'python': ('http://docs.python.org/3/', None),
    'pyalsaaudio': ('https://larsimmisch.github.io/pyalsaaudio/', None),
}


# -- Options for HTML output --------------------------------------------------

#html_theme = 'default'
html_static_path = ['_static']

html_use_modindex = True
html_use_index = True
html_split_index = False
html_show_sourcelink = True

htmlhelp_basename = 'pyspotify'

# -- Options for extlink extension --------------------------------------------

extlinks = {
    'issue': ('https://github.com/mopidy/pyspotify/issues/%s', '#'),
    'ms-issue': (
        'https://github.com/mopidy/mopidy-spotify/issues/%s',
        'mopidy-spotify#'),
}
