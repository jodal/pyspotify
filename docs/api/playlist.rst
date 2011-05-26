Playlists
*********

The :class:`Playlist` class
===========================
.. currentmodule:: spotify

:class:`Playlist` objects are iterable: they are a list of :class:`Track`
objects.

.. class:: Playlist

    Playlist objects.

    .. method:: add_tracks_added_callback(callback[, manager, userdata])

        :param callback:    signature: (manager, :class:`Playlist` p, list of
            :class:`Track` tracks, :class:`int` num_tracks,
            :class:`int` position, :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

        Add this callback if you want to be notified  whenever tracks are added
        to the playlist.

    .. method:: add_tracks_moved_callback(callback[, manager, userdata])

        :param callback:    signature: (manager, :class:`Playlist` p, list of
            :class:`Track` tracks, :class:`int` num_tracks,
            :class:`int` new_position, :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

        Add this callback if you want to be notified whenever tracks are moved
        in the playlist.

    .. method:: add_tracks_removed_callback(callback[, manager, userdata])

        :param callback:    signature: (manager, :class:`Playlist` p, list of
            :class:`Track` tracks, :class:`int` num_tracks,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

        Add this callback if you want to be notified whenever tracks are removed
        from the playlist.

    .. method:: is_collaborative

        :rtype:     :class:`int`
        :returns:   collaborative status for a playlist.

        ..note:: A playlist in collaborative state can be modifed by all
            users, not only the user owning the list.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   wether this playlist has been loaded by the client

    .. method:: name

        :rtype:     string
        :returns:   the name of the playlist.

    .. method:: remove_callback(callback[, userdata])

        Removes the corresponding callback, userdata couple.

    .. method:: remove_tracks(tracks)

        :param tracks:  A list of tracks to be removed from the playlist.
        :type tracks:   list of :class:`Track`
