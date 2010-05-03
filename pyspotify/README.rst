pyspotify 
=========

Copyright 2009-10 Doug Winter
All rights reserved

License information
-------------------

This package is licensed under the Apache License, Version 2.0.  Please see the
file doc/LICENSE for more information.

This product uses SPOTIFY(R) CORE but is not endorsed, certified or otherwise
approved in any way by Spotify. Spotify is the registered trade mark of the
Spotify Group.

Introduction
------------

This package provides a Python interface to Spotify's online music streaming
service.  This package is virtually API complete, and should provide everything
you need to write a spotify client in Python.

The missing parts of the API are: artist browsing, album browsing and the image
handling subsystem.  These will be added soon.

To use this package you will also need libspotify, availably from Spotify here:

    http://developer.spotify.com/en/libspotify/overview/

You will need a Spotify Premium account.  You will also need to apply for, and
receive an API key from spotify.

I include a copy of libspotify in this package, to make use of it easier - in
particular it has some installation issues on Ubuntu that have not been fixed
yet.

Building the software
---------------------

See doc/INSTALL

Trying it out
-------------

Included with this is a simple program, jukebox.py.  Run this with your
credentials and access to an API key, and it will let you browse and play from
your playlists, conduct searches and play from spotify URIs.

