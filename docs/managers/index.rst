Managers
========

.. module:: spotify.manager

The role of the *pyspotify* managers is to help the developper by abstracting
basic operations of the spotify library. They include callbacks that you can
implement if you wish to be notified of particular spotify events.

The one you certainly want to use is the :class:`session manager
<SpotifySessionManager>`, as it handles all login and other basic session
operations.

.. toctree::

    session
    playlist
    container
