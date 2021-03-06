************
Internal API
************

.. warning::

   This page documents pyspotify's internal APIs. Its intended audience is
   developers working on pyspotify itself. You should not use anything you
   find on this page in your own applications.


libspotify CFFI interface
=========================

The `CFFI <http://cffi.readthedocs.io/>`__ wrapper for the full libspotify API
is available as :attr:`spotify.ffi` and :attr:`spotify.lib`.

.. attribute:: spotify.ffi

    :class:`cffi.FFI` instance which knows about libspotify types.

    ::

        >>> import spotify
        >>> spotify.ffi.new('sp_audioformat *')
        <cdata 'struct sp_audioformat *' owning 12 bytes>

.. attribute:: spotify.lib

    Dynamic wrapper around the full libspotify C API.

    ::

        >>> import spotify
        >>> msg = spotify.lib.sp_error_message(spotify.lib.SP_ERROR_OK)
        >>> msg
        <cdata 'char *' 0x7f29fd922cb5>
        >>> spotify.ffi.string(msg)
        'No error'

:attr:`spotify.lib` will always reflect the contents of the
``spotify/api.processed.h`` file in the pyspotify distribution. To update
the API:

#. Update the file ``spotify/api.h`` with the latest header file from
   libspotify.

#. Run the `Invoke <http://www.pyinvoke.org/>`_ task ``preprocess_header``
   defined in ``tasks.py`` by running::

     invoke preprocess_header

   The task will update the ``spotify/api.processed.h`` file.

#. Commit both header files so that they are distributed with pyspotify.


Thread safety utils
===================

.. autofunction:: spotify.serialized


Event emitter utils
===================

.. autoclass:: spotify.utils.EventEmitter


Enumeration utils
=================

.. autoclass:: spotify.utils.IntEnum
    :no-inherited-members:

.. autofunction:: spotify.utils.make_enum


Object loading utils
====================

.. autofunction:: spotify.utils.load


Sequence utils
==============

.. autoclass:: spotify.utils.Sequence
    :no-inherited-members:


String conversion utils
=======================

.. autofunction:: spotify.utils.get_with_fixed_buffer

.. autofunction:: spotify.utils.get_with_growing_buffer

.. autofunction:: spotify.utils.to_bytes

.. autofunction:: spotify.utils.to_bytes_or_none

.. autofunction:: spotify.utils.to_unicode

.. autofunction:: spotify.utils.to_unicode_or_none

.. autofunction:: spotify.utils.to_char

.. autofunction:: spotify.utils.to_char_or_null


Country code utils
==================

.. autofunction:: spotify.utils.to_country

.. autofunction:: spotify.utils.to_country_code
