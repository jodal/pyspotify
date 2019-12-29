*********
Playlists
*********

.. warning::

    The playlists API was broken at 2018-05-24 by a server-side change
    made by Spotify. The functionality was never restored.

    Please use the Spotify Web API to work with playlists.

.. module:: spotify
    :noindex:

.. autoclass:: Playlist

.. autoclass:: PlaylistEvent

.. autoclass:: PlaylistContainer

.. autoclass:: PlaylistContainerEvent

.. autoclass:: PlaylistFolder
    :no-inherited-members:

    .. attribute:: id

        An opaque ID that matches the ID of the :class:`PlaylistFolder` object
        at the other end of the folder.

    .. attribute:: name

        Name of the playlist folder. This is an empty string for the
        :attr:`~PlaylistType.END_FOLDER`.

    .. attribute:: type

        The :class:`PlaylistType` of the folder. Either
        :attr:`~PlaylistType.START_FOLDER` or :attr:`~PlaylistType.END_FOLDER`.

.. autoclass:: PlaylistOfflineStatus
    :no-inherited-members:

.. autoclass:: PlaylistPlaceholder

.. autoclass:: PlaylistTrack

.. autoclass:: PlaylistType
    :no-inherited-members:

.. autoclass:: PlaylistUnseenTracks
