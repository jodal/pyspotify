Artist browsing
***************
.. currentmodule:: spotify

Artist browsers are created by the method
:meth:`browse_artist <Session.browse_artist>` of a :class:`Session <Session>`
object. They are iterable objects.


The :class:`ArtistBrowser` class
================================

.. class:: ArtistBrowser

    ArtistBrowser objects.

    .. note:: A sequence of :class:`Track` objects.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   Wether this artist browser has finished loading metadata.

