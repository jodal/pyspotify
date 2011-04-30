Track subsystem
***************

The :class:`Track` class
========================
.. currentmodule:: spotify

.. class:: Track

    Track objects

    .. method:: album()

        :rtype:     :class:`Album`
        :returns:    The album of this track.

    .. method:: artists()

        :rtype:     List of :class:`Artist`
        :returns:   The artists who performed on this track.

    .. method:: disc()

        :rtype:     :class:`int`
        :returns:   The disc number of this track.

        .. note:: This function returns valid data only for tracks appearing
            in a browse artist or browse album result (otherwise returns 0).

    .. method:: duration()

        :rtype:     :class:`int`
        :returns:   The duration of this track, in milliseconds.

    .. method:: error()

        :rtype:     :class:`int`
        :returns:   An error code associated with this track. For example if it could not load.

    .. method:: index()

        :rtype:     :class:`int`
        :returns:   The position of this track on its disc.

        .. note:: This function returns valid data only for tracks appearing in
            a browse artist or browse album result (otherwise returns 0).

    .. method:: is_loaded()

        :rtype:     :class:`int`
        :returns:   Load status for this track.

        .. note:: If the track is not loaded yet, all other functions operating
            on the track return default values.

    .. method:: name()

        :rtype:     :class:`String`
        :returns:   The name of this track.

    .. method:: popularity()

        :rtype:     :class:`int`
        :returns:   The popularity of this track.

    .. method:: starred(session[, set])

        :param session: The current session.
        :type session:  :class:`Session`
        :param set:     If given, set the starred status of the track.
        :type set:      :class:`bool`
        :rtype:         :class:`bool`
        :returns:       Wether the track is starred or not.

