************
Installation
************

Since pyspotify is a Python wrapper around the libspotify library, pyspotify
necessarily depends on libspotify.


Installing libspotify
=====================

libspotify is provided as a binary download for a selection of operating
systems and CPU architectures from the `libspotify site
<https://developer.spotify.com/technologies/libspotify/>`__. If libspotify
isn't available for your OS or architecture, then you're out of luck and can't
use pyspotify either.

To install libspotify, use one of the options below, or follow the instructions
on the libspotify site and in the README file of the libspotify tarball.


Debian/Ubuntu/Raspbian
----------------------

If you're running a Debian-based Linux distribution, like Ubuntu or Raspbian,
you can get Debian packages of libspotify from `apt.mopidy.com
<https://apt.mopidy.com/>`__. Follow the instructions on the site to add
apt.mopidy.com as a software repository on your system. In summary::

    wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
    sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/mopidy.list
    sudo apt-get update

Then install libspotify::

    sudo apt-get install libspotify-dev


Arch Linux
----------

libspotify is packaged in `AUR
<https://aur.archlinux.org/packages/libspotify/>`_. To install libspotify,
run::

    yaourt -S libspotify


Mac OS X
--------

If you're using `Homebrew <http://brew.sh/>`_, it has a formula for
libspotify::

    brew install libspotify

TODO: Check if pyspotify works with the Mac OS X download option from the
libspotify web site.


Installing pyspotify
====================

You can install pyspotify from PyPI. PyPI may have a pyspotify package
precompiled for your OS and architecture available as a wheel package. To
install it run::

    pip install --pre pyspotify

.. note::

    The ``--pre`` argument to ``pip install`` is needed to make pip 1.5 or
    newer install pre-releases, like the alpha and beta releases of pyspotify
    2.x.

If this fails, then pyspotify probably isn't available prebuilt for your OS and
architecture. In that case, you'll need a C compiler, Python development
headers, and libffi development headers to build pyspotify. When you got that
in place, you can rerun the ``pip`` command to install pyspotify.

Once you have pyspotify installed, you should head over to :doc:`quickstart`
for a short introduction to pyspotify.


Debian/Ubuntu/Raspbian
----------------------

If you're on a Debian-based system, you can install the pyspotify build
dependencies by running::

    sudo apt-get install build-essential python-dev python3-dev libffi-dev


Arch Linux
----------

If you're on Arch Linux, you can install the pyspotify build dependencies by
running::

    sudo pacman -S base-devel

TODO: Check if you need to install libffi headers, etc.


Mac OS X
--------

If you're on Mac OS X, you'll need to install X Code from the Mac App Store to
get the pyspotify build dependencies. If you're using Homebrew, you already
have X Code installed.

TODO: Check if you need to install libffi headers, etc.
