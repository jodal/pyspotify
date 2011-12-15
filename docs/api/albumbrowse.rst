Album browsing
**************
.. currentmodule:: spotify

The :class:`AlbumBrowser` class
===============================

.. class:: AlbumBrowser(album,[ callback[ ,userdata]])

    .. note:: A sequence of :class:`Track` objects.

    Browse an album, calling the callback when the browser's metadata is
    loaded.

    :param album: A spotify album (does not have to be loaded)
    :type album: :class:`Album`
    :param callback: signature : ``(AlbumBrowser browser, Object userdata)``
    :param userdata: any object

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   Wether this album browser has finished loading metadata.

