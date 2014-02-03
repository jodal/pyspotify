***
API
***

.. module:: spotify

The pyspotify API follows the `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__ API closely. Thus,
you can refer to the similarly named functions in the libspotify docs for
further details.


.. attribute:: __version__

    pyspotify's version number in the :pep:`386` format.

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

    :attr:`spotify.lib` will always reflect the contents of the
    ``spotify/api.processed.h`` file in the pyspotify distribution. To update
    the API:

    #. Update the file ``spotify/api.h`` with the latest header file from
       libspotify.

    #. Run the Fabric task ``preprocess_header`` defined in
       ``fabfile.py`` by running::

           fab preprocess_header

       The task will update the ``spotify/api.processed.h`` file.

    #. Commit both header files so that they are distributed with pyspotify.


Error handling
==============

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

.. autoclass:: SessionConfig

.. autoclass:: Session

.. autoclass:: SessionEvent

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

.. autoclass:: AlbumBrowser

.. autoclass:: AlbumType
    :no-inherited-members:


Artists
=======

.. autoclass:: Artist

.. autoclass:: ArtistBrowser

.. autoclass:: ArtistBrowserType
    :no-inherited-members:


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

.. autoclass:: PlaylistContainerEvent

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

.. autoclass:: PlaylistUnseenTracks


Users
=====

.. autoclass:: User


Toplists
========

.. autoclass:: Toplist

.. autoclass:: ToplistRegion
    :no-inherited-members:

.. autoclass:: ToplistType
    :no-inherited-members:


Inbox
=====

.. autoclass:: InboxPostResult
