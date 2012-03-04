Search subsystem
****************

The :class:`Results` class
==========================
.. currentmodule:: spotify

.. class:: Results

    Results corresponding to a search query.

    .. method:: albums

        :rtype:     list of :class:`Album`
        :returns:   albums found by the search.

    .. method:: artists

        :rtype:     list of :class:`Artist`
        :returns:   artists found by the search.

    .. method:: did_you_mean

        :rtype:     string
        :returns:   A query suggestion by Spotify.

    .. method:: error

        :rtype:     :class:`int`
        :returns:   check if an error happened. ``0`` means no error.

    .. method:: is_loaded

        :rtype:     :class:`int`
        :returns:   Wether the results metadata are loaded.

    .. method:: query

        :rtype:     string
        :returns:   the query expression that generated these results.

    .. method:: total_albums

        :rtype:     :class:`int`
        :returns:   the total number of albums available for this search query.

        .. note:: If this value is larger than the interval specified at
            creation of the search object, more search results are available.
            To fetch these, create a new search object with a new interval.

    .. method:: total_artists

        :rtype:     :class:`int`
        :returns:   the total number of artists available for this search query.

        .. note:: If this value is larger than the interval specified at
            creation of the search object, more search results are available.
            To fetch these, create a new search object with a new interval.

    .. method:: total_tracks

        :rtype:     :class:`int`
        :returns:   the total number of tracks available for this search query.

        .. note:: If this value is larger than the interval specified at
            creation of the search object, more search results are available.
            To fetch these, create a new search object with a new interval.

    .. method:: tracks

        :rtype:     list of :class:`Track`
        :returns:   tracks found by the search.


