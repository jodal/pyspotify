Session handling
****************

.. currentmodule:: spotify

The session handling is usually done by inheriting the
:class:`spotify.manager.SpotifySessionManager` class from the
:mod:`spotify.manager` module.  Then the manager's :meth:`connect` method calls
the :func:`spotify.connect` function.

.. function:: connect(session_manager)

    Connect to the Spotify API using a session manager. The callbacks must
    have been defined in that class. See
    :class:`SpotifySessionManager <spotify.manager.SpotifySessionManager>`
    for reference.

    Returns the newly created session as a :class:`spotify.Session` object.


The :class:`Session` class
==========================
.. currentmodule:: spotify

.. class:: Session

    A Spotify session object.

    .. method:: browse_album(album, callback[ ,userdata])

        Browse an album, calling the callback when the browser's metadata is
        loaded.

        :param album: a Spotify album (does not have to be loaded)
        :type album: :class:`Album`
        :param callback: a function with signature :
            ``(AlbumBrowser browser, Object userdata)``
        :param userdata: any object
        :returns: An :class:`AlbumBrowser` object containing the results

        .. deprecated:: 1.7
            Use :class:`AlbumBrowser` instead.


    .. method:: browse_artist(artist, callback[, userdata])

        Browse an artist, calling the callback when the browser's metadata is
        loaded.

        :param artist: a Spotify artist (does not have to be loaded)
        :type artist: :class:`Artist`
        :param callback: a function with signature :
            ``(ArtistBrowser browser, Object userdata)``
        :param userdata: any object
        :returns: An :class:`ArtistBrowser` object containing the results.

        .. deprecated:: 1.7
            Use :class:`ArtistBrowser` instead.


    .. method:: display_name()

        :rtype:     string
        :returns:   the full name for the logged in user.

        Raises :exc:`SpotifyError` if not logged in.

    .. method:: flush_caches

        This will make libspotify write all data that is meant to be stored
        on disk to the disk immediately. libspotify does this periodically
        by itself and also on logout. So under normal conditions this
        should never need to be used.

    .. method:: image_create(id)

        :param string id:   the id of the image to be fetched.
        :returns:           an :class:`Image` object.

        Create an image of album cover art.

    .. method:: is_available(track)

        :param track:   a track
        :type track:    :class:`Track`
        :rtype:         :class:`int`
        :returns:       Wether the track is available for playback.

    .. method:: load(track)

        :param track:   a track
        :type track:    :class:`Track`
        :raises:        :exc:`SpotifyError`

        Load the specified track on the player.

    .. method:: logout()

        Logout from the session.

    .. method:: play(play)

        :param int play: Pause playback if ``0``, else play.

        Play or pause the currently loaded track

    .. method:: playlist_container()

        :rtype:     :class:`PlaylistContainer`
        :returns:   the playlist container for the currently logged in user.

    .. method:: process_events()

        Make the *libspotify* library process any pending event. This should be
        called from the :meth:`notify_main_thread
        <spotify.manager.SpotifySessionManager.notify_main_thread>` session
        callback.

    .. method:: search(query, callback[ ,track_offset=0, track_count=32, album_offset=0, album_count=32, artist_offset=0, artist_count=32, playlist_offset=0, playlist_count=32, search_type='standard', userdata=None])

        :param query:           Query search string
        :param callback:        signature ``(Results results, Object userdata)``
        :param track_offset:    The offset among the tracks of the result
        :param track_count:     The number of tracks to ask for
        :param album_offset:    The offset among the albums of the result
        :param album_count:     The number of albums to ask for
        :param artist_offset:   The offset among the artists of the result
        :param artist_count:    The number of artists to ask for
        :param playlist_offset: The offset among the playlists of the result
        :param playlist_count:  The number of playlists to ask for
        :param search_type:     'standard' or 'suggest'

        :returns:               The search results
        :rtype:                 :class:`Results`


        Conduct a search, calling the callback when the results are available.


    .. method:: seek(offset)

        Seek to *offset* (in milliseconds) in the currently loaded track.

    .. method:: set_preferred_bitrate(bitrate)

        Set the preferred bitrate for the audio stream. ``0`` = 160kbps,
        ``1`` = 320kbps.

    .. method:: starred()

        :rtype:     :class:`Playlist` object.
        :returns:   the playlist of starred tracks for the logged in user.

    .. method:: unload()

        Stop the currently playing track and unloads it from the player.

    .. method:: user_is_loaded()

        Return whether the user is loaded or not, as an *int*.

        If the user is not logged in, this method raises a :exc:`SpotifyError`.

    .. method:: username

        Return a string containing the canonical username for the logged in
        user.

        If the user is not logged in, this method raises a :exc:`SpotifyError`.
