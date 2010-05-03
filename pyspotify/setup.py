#! /usr/bin/env python
#
# Copyright 2009 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
      packages=find_packages(exclude='tests'),
      package_data = {
        '': ['README.rst', 'CHANGES.txt'],
      },
      ext_modules=[
        Extension('spotify._spotify',
                  ['src/module.c', 'src/session.c', 'src/link.c', 'src/track.c', 'src/album.c', 'src/artist.c', 'src/search.c', 'src/playlist.c', 'src/image.c',
],
                  include_dirs=['src'],
                  libraries=['spotify'],
                  library_dirs=["lib"],
                 ),
        Extension('spotify._mockspotify',
                  ['src/mockmodule.c', 'src/session.c', 'src/link.c', 'src/track.c', 'src/album.c', 'src/artist.c', 'src/search.c', 'src/playlist.c', 'src/image.c'],
                  include_dirs=['src'],
                  library_dirs=["lib"],
                 )
      ],
      )


