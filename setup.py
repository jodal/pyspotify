#! /usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

setup(name='pyspotify',
      version='1.0',
      description='Python wrapper for libspotify',
      author='Doug Winter',
      author_email='doug.winter@isotoma.com',
      url='foo',
      packages=find_packages(exclude='tests'),
      ext_modules=[Extension('pyspotify.session', 
                             ['src/session.c'], 
                             libraries=['spotify'],
                             library_dirs=["lib"],
                             ),
                   Extension('pyspotify.mocksession', 
                             ['src/session.c', 
                              'src/mocksession.c'],
                             library_dirs=["lib"],
                             )],
      test_suite="pyspotify.tests.test_all",
      )


