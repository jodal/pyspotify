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


    .. method:: as_album()

        Return this link as an :class:`Album` object.

    .. method:: as_artist()

        Return this link as an :class:`Artist` object.

    .. method:: as_track()

        Return this link as a :class:`Track` object.

    .. staticmethod:: from_album(album)

        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from an :class:`Album` object.

    .. staticmethod:: from_artist(artist)

       :raises: :exc:`SpotifyError`

       Create a new :class:`Link` object from an :class:`Artist` object.

    .. staticmethod:: from_playlist(playlist)

       :raises: :exc:`SpotifyError`

       Create a new :class:`Link` object from a :class:`Playlist` object.

    .. staticmethod:: from_search(results)

       :raises: :exc:`SpotifyError`

       Create a new :class:`Link` object from a :class:`Results` object.

    .. staticmethod:: from_string(s)

        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from a string.
        Raises an exception if the string is not a valid Spotify URI.

    .. staticmethod:: from_track()

        :raises: :exc:`SpotifyError`

        Create a new :class:`Link` object from a :class:`Track` object.

    .. method:: type()

        Return the type of the link as an :class:`int`. Check value
        against the :data:`LINK_*` types.


