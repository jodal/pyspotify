Album browsing
**************
.. currentmodule:: spotify

Album browsers are created by :meth:`Session.browse_album` object. They are
iterable objects.


The :class:`AlbumBrowser` class
===============================

.. class:: AlbumBrowser

    AlbumBrowser objects.

    .. note:: A sequence of :class:`Track` objects.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   Wether this album browser has finished loading metadata.

