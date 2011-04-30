pyspotify
=========

pyspotify is the Python bindings for libspotify.

This is not the original version of pyspotify, as made by `winjer
<http://github.com/winjer/>`_, but an updated version
for use with `Mopidy <http://www.mopidy.com/>`_.

Please see the Mopidy web site for further information on pyspotify.


Upstream notes
==============

Copyright 2009-10 Doug Winter
All rights reserved

License information
-------------------

This package is licensed under the Apache License, Version 2.0.  Please see the
file docs/LICENSE for more information.

This product uses SPOTIFY(R) CORE but is not endorsed, certified or otherwise
approved in any way by Spotify. Spotify is the registered trade mark of the
Spotify Group.

Introduction
------------

This package provides a Python interface to Spotify's online music streaming
service.

To use this package you will also need libspotify, availably from Spotify here:

    http://developer.spotify.com/en/libspotify/overview/

You will need a Spotify Premium account.  You will also need to apply for, and
receive an API key from spotify.

Completion status
-----------------

Pyspotify is very usable, and implements most of the Spotify API. The table
below shows what is done and what is left to be done.



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


Building the software
---------------------

See docs/installation.rst

Trying it out
-------------

Included with this is a simple program, jukebox.py.  Run this with your
credentials and access to an API key, and it will let you browse and play from
your playlists, conduct searches and play from spotify URIs.
