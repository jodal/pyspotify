Artist browsing
***************
.. currentmodule:: spotify

Artist browsers are created by :meth:`Session.browse_artist` object. They are
iterable objects.


The :class:`ArtistBrowser` class
================================

.. class:: ArtistBrowser

    ArtistBrowser objects.

    .. note:: A sequence of :class:`Track` objects.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   Wether this artist browser has finished loading metadata.

