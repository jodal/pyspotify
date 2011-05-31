************
Introduction
************

pyspotify provides a Python interface to `Spotify's <http://www.spotify.com/>`_
online music streaming service.


Completion status
=================

pyspotify is very usable, and implements most of the libspotify 0.0.7 API. The
table below shows what is done and what is left to be done.

==================================  ==================================
Subsystem                           Status
==================================  ==================================
Error handling                      Fully implemented
Session handling                    Fully implemented
Link subsystem                      Fully implemented
Track subsystem                     Fully implemented
Album subsystem                     Fully implemented
Artist subsystem                    Fully implemented
Album browsing                      Fully implemented
Artist browsing                     Fully implemented
Image handling                      Partially implemented
Search subsystem                    Fully implemented
Playlist subsystem                  Partially implemented
User handling                       Not implemented
Toplist handling                    Not implemented
Inbox subsystem                     Not implemented
==================================  ==================================


Requirements
============

To use this package you will also need `libspotify
<http://developer.spotify.com/en/libspotify/overview/>`_, which is available
from Spotify.

You will need a Spotify Premium account. You will also need to apply for, and
receive an API key from Spotify.


Installation
============

Debian package
--------------

For Ubuntu and Debian users, *pyspotify* can be found in the ``python-spotify``
package of the `Mopidy APT archive <http://apt.mopidy.com/>`_.

Arch Linux package
------------------

Install the ``pyspotify-git`` package from the AUR.

Using Pip
---------

The ``pip`` program for installing Python packages is usually found is the
``python-pip`` package of your linux distribution.

To install ``pyspotify``, run as root::

    pip install -U pyspotify

To update an existing installation, simply use the same command.

Using setuptools (latest git version)
-------------------------------------

You will have first to clone the `git repository <http://github.com/mopidy/pyspotify>`_.

On Ubuntu or other Debian-based distributions::

    python setup.py install --install-layout=deb

On other::

    python setup.py install


Trying it out
=============

Included with pyspotify is a simple program, `examples/jukebox.py`.  Run this
with your credentials and access to an API key, and it will let you browse and
play from your playlists, conduct searches and play from Spotify URIs.
