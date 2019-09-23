************
Installation
************

pyspotify is packaged for various operating systems and in multiple Linux
distributions. What way to install pyspotify is best for you depends upon your
OS and/or distribution.


.. _debian-install:

Debian/Ubuntu: Install from apt.mopidy.com
==========================================

The `Mopidy <https://www.mopidy.com/>`_ project runs its own APT archive which
includes pyspotify built for:

- Debian stretch (oldstable), which also works for Ubuntu 16.04 LTS.
- Debian buster (stable), which also works for Ubuntu 18.04 LTS and newer.

The packages are available for multiple CPU architectures: i386, amd64, armel,
and armhf (compatible with Raspbian and all Raspberry Pi models).

To install and receive future updates:

1. Add the archive's GPG key::

       wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -

2. If you run Debian stretch or Ubuntu 16.04 LTS::

       sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/stretch.list

   Or, if you run any newer Debian/Ubuntu distro::

       sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

3. Install pyspotify and all dependencies::

       sudo apt-get update
       sudo apt-get install python-spotify


Arch Linux: Install from AUR
============================

If you are running Arch Linux on x86 or x86_64, you can install pyspotify using
the `python2-pyspotify package
<https://aur.archlinux.org/packages/python2-pyspotify/>`_ found in AUR.

1. To install pyspotify with all dependencies, run::

       yay -S python2-pyspotify

.. note::

   AUR does not provide libspotify for all CPU architectures e.g. arm. See
   :ref:`_source-install` in these cases.


OS X: Install wheel package from PyPI with pip
==============================================

From PyPI, you can install precompiled wheel packages of pyspotify that bundle
libspotify. The packages should work on all combinations of:

- OS X 10.6 and newer
- 32-bit and 64-bit
- Apple-Python, Python.org-Python, Homebrew-Python

1. Make sure you have a recent version of pip, which will default to installing
   a wheel package if available::

       pip install --upgrade pip

2. Install pyspotify::

       pip install pyspotify


OS X: Install from Homebrew
===========================

The `Mopidy <https://www.mopidy.com/>`__ project maintains its own `Homebrew
tap <https://github.com/mopidy/homebrew-mopidy>`_ which includes pyspotify and
its dependencies.

1. Install `Homebrew <http://brew.sh/>`_.

2. Make sure your installation is up to date::

       brew update
       brew upgrade --all

3. Install pyspotify from the mopidy/mopidy tap::

       brew install mopidy/mopidy/python-spotify


.. _source-install:

Install from source
===================

If you are on Linux, but your distro don't package pyspotify, you can install
pyspotify from PyPI using the pip installer. However, since pyspotify is a
Python wrapper around the libspotify library, pyspotify necessarily depends on
libspotify and it must be installed first.


libspotify
----------

libspotify is provided as a binary download for a selection of operating
systems and CPU architectures from our `unofficial libspotify archive
<https://mopidy.github.io/libspotify-archive/>`__. If libspotify
isn't available for your OS or architecture, then you're out of luck and can't
use pyspotify either.

To install libspotify, use one of the options below, or follow the instructions
in the README file of the libspotify tarball.


Debian/Ubuntu
~~~~~~~~~~~~~

If you're running a Debian-based Linux distribution, like Ubuntu,
you can get Debian packages of libspotify from `apt.mopidy.com
<https://apt.mopidy.com/>`__. Follow the instructions :ref:`above
<debian-install>` to make the apt.mopidy.com archive available on your system,
then install libspotify::

    sudo apt-get install libspotify-dev


Arch Linux
~~~~~~~~~~

libspotify for x86 and x86_64 is packaged in `AUR
<https://aur.archlinux.org/packages/libspotify/>`_. To install libspotify,
run::

    yay -S libspotify

.. note::

   AUR only provides libspotify binaries for x86 and x86_64 CPUs. If you
   require libspotify for a different CPU architecture you'll need to download
   it from our `unofficial libspotify archive
   <https://mopidy.github.io/libspotify-archive/>`__ instead.


OS X
~~~~

If you're using `Homebrew <http://brew.sh/>`_, it has a formula for
libspotify in the homebrew/binary tap::

    brew install homebrew/binary/libspotify

.. warning::

   There's an issue with building pyspotify against libspotify on OS X where
   the pyspotify installation fails with "Reason: image not found".

   A known workaround is to create a symlink after installing libspotify, but
   before installing pyspotify::

       ln -s /usr/local/opt/libspotify/lib/libspotify.12.1.51.dylib \
       /usr/local/opt/libspotify/lib/libspotify

   Alternatively, the mopidy/mopidy Homebrew tap has a libspotify formula which
   includes the workaround::

       brew install mopidy/mopidy/libspotify

   For details, or if you have a proper fix for this, see :issue:`130`.


Build tools
-----------

To build pyspotify, you need a C compiler, Python development headers, and
libffi development headers. All of this is easily installed using your system's
package manager.


Debian/Ubuntu
~~~~~~~~~~~~~

If you're on a Debian-based system, you can install the pyspotify build
dependencies by running::

    sudo apt-get install build-essential python-dev python3-dev libffi-dev


Arch Linux
~~~~~~~~~~

If you're on Arch Linux, you can install the pyspotify build dependencies by
running::

    sudo pacman -S base-devel python2 python


OS X
~~~~

If you're on OS X, you'll need to install the Xcode command line developer
tools. Even if you've already installed Xcode from the App Store, e.g. to get
Homebrew working, you should run this command::

    xcode-select --install

.. note::

    If you get an error about ``ffi.h`` not being found when installing the
    cffi Python package, try running the above command.


pyspotify
---------

With libspotify and the build tools in place, you can finally build pyspotify.

To download and build pyspotify from PyPI, run::

    pip install pyspotify

Or, if you have a checkout of the pyspotify git repo, run::

    pip install -e path/to/my/pyspotify/git/clone

Once you have pyspotify installed, you should head over to :doc:`quickstart`
for a short introduction to pyspotify.
