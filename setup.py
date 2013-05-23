from __future__ import unicode_literals

import re

from setuptools import setup, find_packages

try:
    import spotify
except ImportError:
    # We're installing, so cffi isn't available yet
    ext_modules = []
else:
    # We're building bdist, so cffi is available
    ext_modules = [spotify.ffi.verifier.get_extension()]


def get_version(filename):
    init_py = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']


setup(
    name='pyspotify',
    version=get_version('spotify/__init__.py'),
    url='http://pyspotify.mopidy.com/',
    license='Apache License, Version 2.0',
    author='Stein Magnus Jodal',
    author_email='stein.magnus@jodal.no',
    description='Python wrapper for libspotify',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    ext_package='spotify',
    ext_modules=ext_modules,
    install_requires=[
        'cffi >= 0.6',
    ]
)
