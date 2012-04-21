Artist browsing
***************
.. currentmodule:: spotify

The :class:`ArtistBrowser` class
================================

.. class:: ArtistBrowser(artist[, type[, callback[, userdata]]])

    .. note:: A sequence of :class:`Track` objects.

    Browse an artist, calling the callback when the browser's metadata is
    loaded.

    :param artist: a Spotify artist (does not have to be loaded)
    :type artist: :class:`Artist`
    :param type:    this browser's type. One of:

        * ``'full'`` (default):     all data will be fetched (deprecated in
          pyspotify 1.7 / libspotify 11)
        * ``'no_tracks'``:          no information about tracks
        * ``'no_albums'``:          no information about albums (implies ``'no_tracks'``)

        The ``'no_tracks'`` and ``'no_albums'`` browser types also include a
        list of top tracks for this artist.

    :param callback: a function with signature :
        ``(ArtistBrowser browser, Object userdata)``
    :param userdata: any object

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   wether this artist browser has finished loading metadata.

    .. method:: albums

        :rtype:     list of :class:`Album`
        :returns:   the list of albums found while browsing

    .. method:: similar_artists

        :rtype:     list of :class:`Artist`
        :returns:   the list of similar artists found while browsing

    .. method:: tracks

        :rtype:     list of :class:`Track`
        :returns:   the list of tracks found while browsing

    .. method:: tophit_tracks

        :rtype:     list of :class:`Track`
        :returns:   the list of top tracks for this artist found while browsing
