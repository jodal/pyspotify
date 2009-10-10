#! /usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

setup(name='spotify',
      version='1.0',
      description='Python wrapper for libspotify',
      author='Doug Winter',
      author_email='doug.winter@isotoma.com',
      url='foo',
      packages=find_packages(exclude='tests'),
      ext_modules=[
        Extension('spotify._spotify',
                  ['src/module.c', 'src/session.c', 'src/link.c', 'src/track.c', 'src/album.c', 'src/artist.c', 'src/search.c', 'src/playlist.c'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify._mockspotify',
                  ['src/mockmodule.c', 'src/session.c', 'src/link.c', 'src/track.c', 'src/album.c', 'src/artist.c', 'src/search.c', 'src/playlist.c'],
                  library_dirs=["lib"],
                 )
      ],
      )


