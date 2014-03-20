from __future__ import unicode_literals

import re

from distutils.command.build import build
from setuptools import setup, find_packages


def read_file(filename):
    with open(filename) as fh:
        return fh.read()


def get_version(filename):
    init_py = read_file(filename)
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']


class cffi_build(build):
    """This is a shameful hack to ensure that cffi is present when we specify
    ext_modules. We can't do this eagerly because setup_requires hasn't run
    yet.
    """
    def finalize_options(self):
        from spotify import ffi
        self.distribution.ext_modules = [ffi.verifier.get_extension()]
        build.finalize_options(self)


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
    ext_package='spotify',
    zip_safe=False,
    include_package_data=True,
    install_requires=['cffi >= 0.7'],
    setup_requires=['cffi >= 0.7'],
    cmdclass={'build': cffi_build},
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
)
