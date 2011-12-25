************
Introduction
************

pyspotify provides a Python interface to `Spotify's <http://www.spotify.com/>`_
online music streaming service.


Completion status
=================

pyspotify is very usable, and implements most of the libspotify 0.0.8 API. The
table below shows what is done and what is left to be done.

==================================  ==================================
Subsystem                           Status
==================================  ==================================
Error handling                      Complete
Session handling                    Complete
Link subsystem                      Complete
Track subsystem                     Complete
Album subsystem                     Complete
Artist subsystem                    Complete
Album browsing                      Complete
Artist browsing                     Complete
Image handling                      Incomplete
Search subsystem                    Complete
Playlist subsystem                  Incomplete
User handling                       Complete
Toplist handling                    Complete
Inbox subsystem                     Not available
Offline synchronization             Not available
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

Using Pip (latest stable release)
---------------------------------

The ``pip`` program for installing Python packages is usually found in the
``python-pip`` package of your Linux distribution.

To install ``pyspotify``, run::

    sudo pip install -U pyspotify

To update an existing installation, simply use the same command.

Using Pip (latest development version)
--------------------------------------

To install the very latest git version of pyspotify::

    sudo pip install -U pyspotify==dev

Using setuptools (latest git version)
-------------------------------------

You will have first to clone the `git repository <http://github.com/mopidy/pyspotify>`_.

Then to install it::

    sudo python setup.py install


Trying it out
=============

Included with pyspotify is a simple program, ``examples/jukebox.py``.  Run this
with your credentials and access to an API key, and it will let you browse and
play from your playlists, conduct searches and play from Spotify URIs.
