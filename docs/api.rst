*************
pyspotify API
*************

.. module:: spotify

The pyspotify API follows the `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__ API as closely as
possible. Thus, you can refer to the similarly named functions in the
libspotify docs for further details.


.. attribute:: __version__

    pyspotify's :pep:`396` version number.

    ::

        >>> import spotify
        >>> spotify.__version__
        '2.0.0'


Low level API
=============

The `CFFI <http://cffi.readthedocs.org/>`__ wrapper for the full libspotify API
is available directly. You should never need to use it, but if there's a
bleeding edge feature in libspotify that pyspotify hasn't been updated to
support yet, you'll find what you need to use it from Python here.

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

    Will always reflect the contents of the ``spotify/api.processed.h`` file in
    the pyspotify distribution. To update the API:

    #. Update the file ``spotify/api.h`` with the latest header file from
       libspotify.

    #. Run the Fabric task ``preprocess_header`` defined in
       ``fabfile.py`` by running::

           fab preprocess_header

       The task will update the ``spotify/api.processed.h`` file.

    #. Commit both header files so that they are distributed with pyspotify.


Logging
=======

pyspotify uses Python's standard :mod:`logging` module for logging. All log
records emitted by pyspotify are issued to the logger named "spotify", or a
sublogger of it.

Out of the box, pyspotify is set up with :class:`logging.NullHandler` as the
only log record handler. This is the recommended approach for logging in
libraries, so that the application developer using the library will have full
control over how the log records from the library will be exposed to the
application's users. In other words, if you want to see the log records from
pyspotify anywhere, you need to add a useful handler to the root logger or the
logger named "spotify" to get any log output from pyspotify. The defaults
provided by :meth:`logging.basicConfig` is enough to get debug log statements
out of pyspotify::

    import logging
    logging.basicConfig(level=logging.DEBUG)

If your application is already using :mod:`logging`, and you want debug log
output from your own application, but not from pyspotify, you can ignore debug
log messages from pyspotify by increasing the threshold on the "spotify" logger
to "info" level or higher::

    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spotify').setLevel(logging.INFO)

For more details on how to use :mod:`logging`, please refer to the Python
standard library documentation.


Text encoding
=============

libspotify encodes all text as UTF-8. pyspotify converts the UTF-8 bytestrings
to Unicode strings before returning them to you, so you don't have to be
worried about text encoding.

Similarly, pyspotify will convert any string you give it from Unicode to UTF-8
encoded bytestrings before passing them on to libspotify. The only exception is
file system paths, which is passed directly to libspotify. This is in case you
have a file system which doesn't use UTF-8 encoding for file names.


Thread safety
=============

TODO: Explain that libspotify isn't threadsafe. You must either use a single
thread to call pyspotify methods, or protect all pyspotify API usage with a
single lock.


Error handling
==============

Where many libspotify functions return error codes that must be checked after
each and every function call, pyspotify raises the :exc:`spotify.Error`
exception instead. This helps you to not accidentally swallow and hide errors
when using pyspotify.

.. autoexception:: Error
    :no-undoc-members:
    :no-inherited-members:

.. autoclass:: ErrorType
    :no-inherited-members:

.. autoexception:: LibError
    :no-undoc-members:
    :no-inherited-members:

.. autoexception:: Timeout
    :no-undoc-members:
    :no-inherited-members:


Sessions
========

.. autoclass:: SessionCallbacks

.. autoclass:: SessionConfig

.. autoclass:: Session

.. autoclass:: spotify.session.Player


Connection
==========

.. autoclass:: spotify.session.Offline

.. autoclass:: ConnectionRule
    :no-inherited-members:

.. autoclass:: ConnectionState
    :no-inherited-members:

.. autoclass:: ConnectionType
    :no-inherited-members:

.. autoclass:: OfflineSyncStatus


Audio
=====

.. autoclass:: AudioBufferStats
    :no-inherited-members:

    .. autoattribute:: samples

    .. autoattribute:: stutter

.. autoclass:: AudioFormat

.. autoclass:: Bitrate
    :no-inherited-members:

.. autoclass:: SampleType
    :no-inherited-members:


Links
=====

.. autoclass:: Link

.. autoclass:: LinkType
    :no-inherited-members:


Tracks
======

.. autoclass:: Track

.. autoclass:: LocalTrack
    :no-inherited-members:

.. autoclass:: TrackAvailability
    :no-inherited-members:

.. autoclass:: TrackOfflineStatus
    :no-inherited-members:


Albums
======

.. autoclass:: Album

.. autoclass:: AlbumType
    :no-inherited-members:

TODO: Album browsing


Artists
=======

.. autoclass:: Artist

TODO: Artist browsing


Images
======

.. autoclass:: Image

.. autoclass:: ImageFormat
    :no-inherited-members:

.. autoclass:: ImageSize
    :no-inherited-members:


Search
======

.. autoclass:: Search

.. autoclass:: SearchPlaylist
    :no-inherited-members:

    .. autoattribute:: name

    .. autoattribute:: uri

    .. autoattribute:: image_uri

.. autoclass:: SearchType
    :no-inherited-members:


Social
======

.. autoclass:: spotify.session.Social

.. autoclass:: ScrobblingState
    :no-inherited-members:

.. autoclass:: SocialProvider
    :no-inherited-members:


Playlists
=========

.. autoclass:: Playlist

.. autoclass:: PlaylistContainer

.. autoclass:: PlaylistFolder
   :no-inherited-members:

   .. autoattribute:: id

   .. autoattribute:: name

   .. autoattribute:: type

.. autoclass:: PlaylistOfflineStatus
    :no-inherited-members:

.. autoclass:: PlaylistTrack

.. autoclass:: PlaylistType
    :no-inherited-members:


Users
=====

.. autoclass:: User


Toplists
========

TODO: Implement

.. autoclass:: ToplistRegion
    :no-inherited-members:

.. autoclass:: ToplistType
    :no-inherited-members:


Inbox
=====

.. autoclass:: InboxPostResult
