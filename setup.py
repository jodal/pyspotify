from setuptools import setup

setup(
    # XXX Setting cffi_modules in setup.cfg does not have any effect.
    cffi_modules=["spotify/_spotify_build.py:ffi"]
)
