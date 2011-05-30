Playlist containers
*******************

The :class:`PlaylistContainer` class
====================================
.. currentmodule:: spotify

The playlist container contains all the playlists attached to a session.
It is a list of :class:`Playlist` objects.

.. class:: PlaylistContainer

    .. method:: add_loaded_callback(callback[, manager, userdata]):

        :param callback:    signature: (manager, :class:`PlaylistContainer` pc,
            :class:`Object` userdata).
        :param userdata:    any object you would like to access in the callback.

        The callback will be called when all metadata in the playlist container
        has finished loading.

    .. method:: add_playlist_added_callback(callback[, manager , userdata]):

        :param callback:    signature: (manager, :class:`PlaylistContainer` pc,
            :class:`Playlist`: p, :class:`int` position,
            :class:`Object` userdata).
        :param userdata:    any object you would like to access in the callback.

        The callback will be called when a playlist is added to the playlist
        container.

    .. method:: add_playlist_moved_callback(callback[, manager, userdata]):

        :param callback:    signature: (manager, :class:`PlaylistContainer` pc,
            :class:`Playlist` p, :class:`int` position,
            :class:`int` new_position, :class:`Object` userdata).
        :param userdata:    any object you would like to access in the callback.

        The callback will be called when a playlist is moved from *position* to
        *new_position*.

    .. method:: add_playlist_removed_callback(callback[, manager, userdata]):

        :param callback:    signature: (manager, :class:`PlaylistContainer` pc,
            :class:`Playlist` p, :class:`int` position,
            :class:`Object` userdata).
        :param userdata:    any object you would like to access in the callback.

        The callback will be called when a playlist is removed from the
        container.
