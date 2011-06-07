Managers
========

.. module:: spotify.manager

The role of the pyspotify *managers* is to help the developer by abstracting
basic operations of the Spotify library. They include callbacks that you can
implement if you wish to be notified of particular Spotify events.

The one you certainly want to use is the :class:`SpotifySessionManager`, as it
handles all login and other basic session operations.

.. toctree::

    session
    playlist
    container
