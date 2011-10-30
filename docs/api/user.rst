Users
*****
.. currentmodule:: spotify

.. class:: User

    User objects

    .. method:: is_loaded

        :rtype:     :class:`bool`
        :returns:   wether the user is loaded.

    .. method:: canonical_name

        :rtype:     :class:`unicode`
        :returns:   the canonical name of the user.

    .. method:: display_name

        :rtype:     :class:`unicode`
        :returns:   the display name of the user, or the canonical name if
            not loaded.
