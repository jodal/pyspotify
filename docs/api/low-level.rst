*************
Low level API
*************

The `CFFI <http://cffi.readthedocs.org/>`__ wrapper for the full libspotify API
is available directly. You should never need to use it, but if there's a
bleeding edge feature in libspotify that pyspotify hasn't been updated to
support yet, you'll find what you need to use it from Python here.

.. module:: spotify

.. attribute:: ffi

    :class:`cffi.FFI` instance which knows about libspotify types.

    ::

        >>> import spotify
        >>> spotify.ffi.new('sp_audioformat *')
        <cdata 'struct sp_audioformat *' owning 12 bytes>

.. attribute:: lib

    Dynamic wrapper around the full libspotify C API.

    ::

        >>> import spotify
        >>> msg = spotify.lib.sp_error_message(spotify.lib.SP_ERROR_OK)
        >>> msg
        <cdata 'char *' 0x7f29fd922cb5>
        >>> spotify.ffi.string(msg)
        'No error'

TODO: Document @serialized decorator?


Updating the low-level API
==========================

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
