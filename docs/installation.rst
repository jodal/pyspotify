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
use pyspotify either. To install libspotify, follow the instructions on the
libspotify site and in the README file of the libspotify tarball.

If you're running a Debian-based Linux distribution, like Ubuntu, you can get
Debian packages of libspotify from `apt.mopidy.com
<https://apt.mopidy.com/>`__. Follow the instructions on the site to add
apt.mopidy.com as a software repository on your system, and then run::

    sudo apt-get install libspotify-dev


Installing pyspotify
====================

.. warning::

   This section is mostly bogus until the first release of pyspotify 2 is
   uploaded to PyPI. You should install from the Git repo for now.

You can install pyspotify from PyPI. PyPI may have a pyspotify package
precompiled for your OS and architecture available as a wheel package. To
install it run::

    pip install --use-wheel pyspotify

If pyspotify isn't available prebuilt for your OS and architecture, you'll
need a C compiler, Python development headers and libffi development headers
to build pyspotify. 

If you're on a Debian-based system, you can install these by running::

    sudo apt-get install build-essential python-dev python3-dev libffi-dev

Then you can build pyspotify from source::

    pip install pyspotify

Once you have pyspotify installed, you should head over to :doc:`quickstart`
for a short introduction to pyspotify.
