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
        Extension('spotify.session',
                  ['src/session.c'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify.link',
                  ['src/link.c'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify.album',
                  ['src/album.c'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify.artist',
                  ['src/artist.c'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify.search',
                  ['src/search.c'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify.mocksession',
                  ['src/session.c',
                  'src/mocksession.c'],
                  library_dirs=["lib"],
                 )
      ],
      )


