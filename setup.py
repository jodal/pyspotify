from __future__ import unicode_literals

import re


from setuptools import find_packages, setup


def read_file(filename):
    with open(filename) as fh:
        return fh.read()


def get_version(filename):
    init_py = read_file(filename)
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
    long_description=read_file('README.rst'),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    setup_requires=['cffi >= 1.0.0'],
    cffi_modules=['spotify/_spotify_build.py:ffi'],
    install_requires=['cffi >= 1.0.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
)
