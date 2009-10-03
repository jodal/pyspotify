#! /usr/bin/env python

from distutils.core import setup, Extension

setup(name='pyspotify',
      version='1.0',
      description='Python wrapper for libspotify',
      author='Doug Winter',
      author_email='doug.winter@isotoma.com',
      url='foo',
      packages=['pyspotify'],
      ext_modules=[Extension('_spotify', ['src/spotify.c'], libraries=['spotify'])],
      )


