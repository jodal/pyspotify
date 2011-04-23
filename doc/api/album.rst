Album subsystem
***************

The :class:`Album` class
========================
.. currentmodule:: spotify

.. class:: Album

    Album objects

    .. data::   ALBUM

    .. data::   SINGLE

    .. data::   COMPILATION

    .. data::   UNKNOW

    .. method:: artist

        :rtype:     :class:`Artist`
        :returns:   the artist associated with this album

    .. method:: cover

        :rtype:     string
        :returns:   the id of the cover data associated with this album

    .. method:: is_available

        :rtype:     :class:`int`
        :returns:   ``1`` if the album is available, ``0`` if not.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   ``1`` if this album has been loaded by the client,
            ``0`` if not.

    .. method:: name

        :rtype:     string
        :returns:   the name of the album.

    .. method:: type

        :rtype:     :class:`int`
        :returns:   the type of the album.

        You can check the value against one of ALBUM, SINGLE, COMPILATION
        or UNKNOWN.

    .. method:: year

        :rtype:     :class:`int`
        :returns:   the year in which the album was released.

