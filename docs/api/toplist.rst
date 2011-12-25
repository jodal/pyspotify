Toplists
********
.. currentmodule:: spotify

.. class:: ToplistBrowser (type, region[, callback, userdata])

    A ToplistBrowser object.

    The browser is a sequence of :class:`spotify.Album`,
    :class:`spotify.Artist` or :class:`spotify.Track` depending on the *type*
    argument given when creating the object.

    :param type: one of ``'albums'``, ``'artists'`` or ``'tracks'``.

    :param region: one of:

        * ``'all'`` for global toplists
        * a two letters country code (e.g ``'SE'``, ``'FR'``)
        * ``'current'`` for the current logged in user's toplists
        * a :class:`spotify.User` object to see this user's toplists

    :param callback: a function with signature (ToplistBrowser tb, userdata)
    :param userdata: any object you would like to access in the callback

    .. method:: is_loaded()

        :returns:   ``True`` if the object's metadata is loaded.

    .. method:: error()

        :returns:   None or an error message associated with the error.

