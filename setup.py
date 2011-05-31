#! /usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

setup(name='pyspotify',
      version='1.1',
      description='Python wrapper for libspotify',
      long_description= open("README.rst").read(),
      author='Doug Winter',
      author_email='doug.winter@isotoma.com',
      url='http://pypi.python.org/pypi/spotify',
      zip_safe=False,
      test_suite="nose.collector",
      packages=find_packages(exclude='tests'),
      package_data = {
        '': ['README.rst', 'CHANGES.txt'],
      },
      ext_modules=[
        Extension('spotify._spotify',
                  ['src/module.c',
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
                   'src/image.c',
                   'src/pyspotify.c',
                  ],
                  include_dirs=['src'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify._mockspotify',
                  ['src/mockmodule.c',
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
                   'src/image.c',
                   'src/pyspotify.c'
                  ],
                  include_dirs=['src'],
                  library_dirs=["lib"],
                 )
      ],
      )


