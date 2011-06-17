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

    .. method:: full_name

        :rtype:     :class:`unicode`
        :returns:   the full name of the user, or `None` if not loaded.

    .. method:: picture

        :rtype:     :class:`unicode`
        :returns:   an url to this user’s picture.

    .. method:: relation

        :rtype:     :class:`int`
        :returns:   the current user’s relation type with this user.

        .. note::   Compare with one of :ref:`user-relation-types`.
