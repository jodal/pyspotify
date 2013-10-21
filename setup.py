#! /usr/bin/env python

from distutils.core import setup, Extension
import os
import re
import sys


def get_version():
    init_py = open('spotify/__init__.py').read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


def with_mock():
    """
    Checks whether the user wants to build the mockmodule (off by default).
    """
    try:
        sys.argv.remove('--with-mock')
        return True
    except ValueError:
        return False


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
project_dir = 'spotify'

for dirpath, dirnames, filenames in os.walk(project_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append(
            [dirpath, [os.path.join(dirpath, f) for f in filenames]])

common_src_files = [
    'src/session.c',
    'src/link.c',
    'src/track.c',
    'src/album.c',
    'src/albumbrowser.c',
    'src/artist.c',
    'src/artistbrowser.c',
    'src/search.c',
    'src/playlist.c',
    'src/playlistcontainer.c',
    'src/playlistfolder.c',
    'src/image.c',
    'src/user.c',
    'src/pyspotify.c',
    'src/toplistbrowser.c',
]

mock_src_files = [
    'libmockspotify/albumbrowse.c',
    'libmockspotify/album.c',
    'libmockspotify/artistbrowse.c',
    'libmockspotify/artist.c',
    'libmockspotify/error.c',
    'libmockspotify/event.c',
    'libmockspotify/image.c',
    'libmockspotify/inbox.c',
    'libmockspotify/libmockspotify.c',
    'libmockspotify/link.c',
    'libmockspotify/player.c',
    'libmockspotify/playlist.c',
    'libmockspotify/playlistcontainer.c',
    'libmockspotify/search.c',
    'libmockspotify/session.c',
    'libmockspotify/toplistbrowse.c',
    'libmockspotify/track.c',
    'libmockspotify/urlcode.c',
    'libmockspotify/user.c',
    'libmockspotify/util.c',
]

if 'darwin' in sys.platform:
    spotify_library_config = {
        'extra_link_args': ['-framework', 'libspotify']
    }
else:
    spotify_library_config = {
        'libraries': ['spotify']
    }

spotify_ext = Extension(
    'spotify._spotify',
    ['src/module.c'] + common_src_files,
    include_dirs=['src'],
    **spotify_library_config)

mockspotify_ext = Extension(
    'spotify._mockspotify',
    mock_src_files + ['src/mockmodule.c'] + common_src_files,
    include_dirs=['src', 'libmockspotify'])

modules = [spotify_ext]
if with_mock():
    modules.append(mockspotify_ext)

setup(
    name='pyspotify',
    version=get_version(),
    description='Python wrapper for libspotify',
    long_description=open('README.rst').read(),
    author='Doug Winter',
    author_email='doug.winter@isotoma.com',
    url='http://pyspotify.mopidy.com/',
    packages=packages,
    data_files=data_files,
    ext_modules=modules,
)
