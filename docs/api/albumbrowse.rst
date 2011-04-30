Album browsing
**************
.. currentmodule:: spotify

Album browsers are created by the method
:meth:`browse_album <Session.browse_album>` of a :class:`Session <Session>`
object. They are iterable objects.


The :class:`AlbumBrowser` class
===============================

.. class:: AlbumBrowser

    AlbumBrowser objects.

    .. note:: A sequence of :class:`Track` objects.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   Wether this album browser has finished loading metadata.

