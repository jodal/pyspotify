Artist browsing
***************
.. currentmodule:: spotify

The :class:`ArtistBrowser` class
================================

.. class:: ArtistBrowser(artist[, callback[, userdata]])

    .. note:: A sequence of :class:`Track` objects.

    Browse an artist, calling the callback when the browser's metadata is
    loaded.

    :param artist: a Spotify artist (does not have to be loaded)
    :type artist: :class:`Artist`
    :param callback: a function with signature :
        ``(ArtistBrowser browser, Object userdata)``
    :param userdata: any object

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   wether this artist browser has finished loading metadata.

