from __future__ import unicode_literals

import re

from distutils.command.build import build

from setuptools import find_packages, setup
from setuptools.command.install import install


def read_file(filename):
    with open(filename) as fh:
        return fh.read()


def get_version(filename):
    init_py = read_file(filename)
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']


class CFFIBuild(build):

    def finalize_options(self):
        from spotify import ffi
        self.distribution.ext_modules = [ffi.verifier.get_extension()]
        build.finalize_options(self)


class CFFIInstall(install):

    def finalize_options(self):
        from spotify import ffi
        self.distribution.ext_modules = [ffi.verifier.get_extension()]
        install.finalize_options(self)


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
    install_requires=[
        'cffi >= 0.7',
    ],
    setup_requires=[
        'cffi >= 0.7'
    ],
    cmdclass={
        'build': CFFIBuild,
        'install': CFFIInstall,
    },
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
