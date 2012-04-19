Spotify links (URIs)
********************
.. currentmodule:: spotify


The :class:`Link` class
=======================

.. class:: Link

    Link objects

    .. data:: LINK_INVALID

        Link type not valid - default until the library has parsed the link,
        or when parsing failed.

    .. data:: LINK_TRACK

    .. data:: LINK_ALBUM

    .. data:: LINK_ARTIST

    .. data:: LINK_SEARCH

    .. data:: LINK_PLAYLIST

    .. method:: __str__()

        Return the link as a string in the Spotify format.

        Example: ``spotify:track:5st5644IlBmKiiRE73UsoZ``

    .. method:: type()

        Return the type of the link as an :class:`int`. Check value
        against the :data:`LINK_*` types.

    .. method:: as_album()

        :return: the link as an :class:`Album` object.
        :rtype: :class:`Album`

    .. method:: as_artist()

        :return: the link as an :class:`Artist` object.
        :rtype: :class:`Artist`

    .. method:: as_track()

        :return: the link as a :class:`Track` object.
        :rtype: :class:`Track`

    .. staticmethod:: from_album(album)

        :param album: an album
        :type album: :class:`Album`
        :return: link to the album
        :rtype: :class:`Link`
        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from an :class:`Album` object.

    .. staticmethod:: from_artist(artist)

        :param artist: an artist
        :type artist: :class:`Artist`
        :return: link to the artist
        :rtype: :class:`Link`
        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from an :class:`Artist` object.

    .. staticmethod:: from_playlist(playlist)

        :param playlist: a playlist
        :type playlist: :class:`Playlist`
        :return: link to the playlist
        :rtype: :class:`Link`
        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from a :class:`Playlist` object.

    .. staticmethod:: from_search(results)

        :param results: a result set
        :type results: :class:`Results`
        :return: link to the result set
        :rtype: :class:`Link`
        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from a :class:`Results` object.

    .. staticmethod:: from_string(s)

        :param s: a Spotify URI
        :type s: :class:`string`
        :return: link to the same resource as the URI string
        :rtype: :class:`Link`
        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from a string.
        Raises an exception if the string is not a valid Spotify URI.

    .. staticmethod:: from_track(track[, offset])

        :param track: a track
        :type track: :class:`Track`
        :param offset: offset in milliseconds from the start of the track
        :type offset: :class:`int`
        :return: link to the result set
        :rtype: :class:`Link`
        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from a :class:`Track` object, and
        optionally a time offset in milliseconds from the start of the track.
