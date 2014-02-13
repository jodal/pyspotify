from __future__ import unicode_literals

import re

from distutils.command.build import build
from setuptools import setup, find_packages


def get_version(filename):
    init_py = open(filename).read()
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
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    ext_package='spotify',
    include_package_data=True,
    install_requires=['cffi >= 0.7'],
    setup_requires=['cffi >= 0.7'],
    zip_safe=False,
    cmdclass={'build': cffi_build}
)
