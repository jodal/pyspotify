Playlists
*********

The :class:`Playlist` class
===========================
.. currentmodule:: spotify

:class:`Playlist` objects are iterable: they are a list of :class:`Track`
objects.

.. class:: Playlist

    Playlist objects.

    .. method:: add_tracks(position, tracks)

        :param position:    where to add the tracks in the playlist
        :type position:     :class:`int`
        :param tracks:      tracks to add to the playlist
        :type tracks:       list of :class:`Track`

    .. method:: add_tracks_added_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p, list of
            :class:`Track` tracks, :class:`int` position,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_tracks_moved_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p, list of
            :class:`Track` tracks, :class:`int` new_position,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_tracks_removed_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p, list of
            :class:`Track` tracks, :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_playlist_renamed_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_playlist_state_changed_callback(callback[, \
        userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback


        Called when state changed for a playlist.

        There are three states that trigger this callback:

        - Collaboration for this playlist has been turned on or off
        - The playlist started having pending changes, or all pending
            changes have now been committed
        - The playlist started loading, or finished loading


    .. method:: add_playlist_update_in_progress_callback(callback[, \
        userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`bool` done, :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

        Called when a playlist is updating or is done updating.

        This is called before and after a series of changes are applied to the
        playlist. It allows e.g. the user interface to defer updating until the
        entire operation is complete.

    .. method:: add_playlist_metadata_updated_callback(callback[, \
        userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_track_created_changed_callback(callback[, \
        userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`int` position, :class:`User` user, :class:`int` when,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

        *user* is the new user information and *when* is a time in seconds
        since the UNIX Epoch.

    .. method:: add_track_message_changed_callback(callback[, \
        userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`int` position, :class:`unicode` message,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_track_seen_changed_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`int` position, :class:`bool` seen,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_description_changed_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`unicode` description, :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_subscribers_changed_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: add_image_changed_callback(callback[, userdata])

        :param callback:    signature: (:class:`Playlist` p,
            :class:`str` image_id, :class:`Object` userdata)
        :param userdata:    any object you would like to access in the callback

    .. method:: is_collaborative

        :rtype:     :class:`int`
        :returns:   collaborative status for a playlist.

        .. note:: A playlist in collaborative state can be modifed by all
            users, not only the user owning the list.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   wether this playlist has been loaded by the client

    .. method:: name

        :rtype:     string
        :returns:   the name of the playlist.

    .. method:: rename(name)

        :param name:    the new name
        :type name:     :class:`unicode`

    .. method:: remove_callback(callback[, userdata])

        Removes the corresponding callback, userdata couple.

    .. method:: remove_tracks(tracks)

        :param tracks:  A list of tracks to be removed from the playlist.
        :type tracks:   list of :class:`Track`
