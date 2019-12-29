**********
Quickstart
**********

This guide will quickly introduce you to some of the core features of
pyspotify. It assumes that you've already installed pyspotify. If you do not,
check out :doc:`installation`. For a complete reference of what pyspotify
provides, refer to the :doc:`api/index`.


Application keys
================

Every app that use libspotify needs its own libspotify application key.
Application keys can be obtained automatically and free of charge from Spotify.

#. Go to the `Spotify developer pages <https://developer.spotify.com/>`__ and
   login using your Spotify account.

#. Find the `libspotify application keys
   <https://developer.spotify.com/technologies/libspotify/keys/>`__ management
   page and request an application key for your application.

#. Once the key is issued, download the "binary" version. The "C code" version
   of the key will not work with pyspotify.

#. If you place the application key in the same directory as your application's
   main Python file, pyspotify will automatically find it and use it. If you
   want to keep the application key in another location, you'll need to set
   :attr:`~spotify.Config.application_key` in your session config or call
   :meth:`~spotify.Config.load_application_key_file` to load the session key
   file correctly.


Creating a session
==================

Once pyspotify is installed and the application key is in place, we can start
writing some Python code. Almost everything in pyspotify requires a
:class:`~spotify.Session`, so we'll start with creating a session with the
default config::

    >>> import spotify
    >>> session = spotify.Session()

All config must be done before the session is created. Thus, if you need to
change any config to something else than the default, you must create a
:class:`~spotify.Config` object first, and then pass it to the session::

    >>> import spotify
    >>> config = spotify.Config()
    >>> config.user_agent = 'My awesome Spotify client'
    >>> config.tracefile = b'/tmp/libspotify-trace.log'
    >>> session = spotify.Session(config)


Text encoding
=============

libspotify encodes all text as UTF-8. pyspotify converts the UTF-8 bytestrings
to Unicode strings before returning them to you, so you don't have to be
worried about text encoding.

Similarly, pyspotify will convert any string you give it from Unicode to UTF-8
encoded bytestrings before passing them on to libspotify. The only exception is
file system paths, like :attr:`~spotify.Config.tracefile` above, which is
passed directly to libspotify. This is in case you have a file system which
doesn't use UTF-8 encoding for file names.


Login and event processing
==========================

With a session we can do a few things, like creating objects from Spotify
URIs::

    >>> import spotify
    >>> session = spotify.Session()
    >>> album = session.get_album('spotify:album:0XHpO9qTpqJJQwa2zFxAAE')
    >>> album
    Album(u'spotify:album:0XHpO9qTpqJJQwa2zFxAAE')
    >>> album.link
    Link(u'spotify:album:0XHpO9qTpqJJQwa2zFxAAE')
    >>> album.link.uri
    u'spotify:album:0XHpO9qTpqJJQwa2zFxAAE'

But that's mostly how far you get with a fresh session. To do more, you need to
login to the Spotify service using a Spotify account with the Premium
subscription.

.. warning::

    pyspotify and all other libspotify applications required a Spotify Premium
    subscription.

    The Free Spotify subscription, or the old Unlimited subscription, will not
    work with pyspotify or any other applications using libspotify.

::

    >>> import spotify
    >>> session = spotify.Session()
    >>> session.login('alice', 's3cretpassword')

For alternative ways to login, refer to the :meth:`~spotify.Session.login`
documentation.

The :meth:`~spotify.Session.login` method is asynchronous, so we must ask the
session to :meth:`~spotify.Session.process_events` until the login has
succeeded or failed::

    >>> session.connection.state
    <ConnectionState.LOGGED_OUT: 0>
    >>> session.process_events()
    >>> session.connection.state
    <ConnectionState.OFFLINE: 1>
    >>> session.process_events()
    >>> session.connection.state
    <ConnectionState.LOGGED_IN: 1>

.. note::

    The connection state is a representation of both your authentication state
    and your offline mode. If libspotify has cached your user object from a
    previous session, it may authenticate you without a connection to Spotify's
    servers. Thus, you may very well be logged in, but still offline.

    The connection state in the above example goes from the ``LOGGED_OUT``
    state, to ``OFFLINE``, to ``LOGGED_IN``. If libspotify hasn't cached any
    information about your Spotify user account, the connection state will
    probably go directly from ``LOGGED_OUT`` to ``LOGGED_IN``. Your application
    should be prepared for this.

    For more details, see the :attr:`session.connection.state
    <spotify.connection.Connection.state>` documentation.

We only called :meth:`~spotify.Session.process_events` twice, which may not be
enough to get to the :attr:`~spotify.ConnectionState.LOGGED_IN` connection
state. A more robust solution is to call it repeatedly until the
:attr:`~spotify.SessionEvent.CONNECTION_STATE_UPDATED` event is emitted on the
:class:`~spotify.Session` object and :attr:`session.connection.state
<spotify.connection.Connection.state>` is
:attr:`~spotify.ConnectionState.LOGGED_IN`::

    >>> import threading
    >>> logged_in_event = threading.Event()
    >>> def connection_state_listener(session):
    ...     if session.connection.state is spotify.ConnectionState.LOGGED_IN:
    ...         logged_in_event.set()
    ...
    >>> session = spotify.Session()
    >>> session.on(
    ...     spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    ...     connection_state_listener)
    ...
    >>> session.login('alice', 's3cretpassword')
    >>> session.connection.state
    <ConnectionState.LOGGED_OUT: 0>
    >>> while not logged_in_event.wait(0.1):
    ...     session.process_events()
    ...
    >>> session.connection.state
    <ConnectionState.LOGGED_IN: 1>
    >>> session.user
    User(u'spotify:user:alice')

This solution works properly, but is a bit tedious. pyspotify provides an
:class:`~spotify.EventLoop` helper thread that can make the
:meth:`~spotify.Session.process_events` calls in the background. With it
running, we can simplify the login process::

    >>> import threading
    >>> logged_in_event = threading.Event()
    >>> def connection_state_listener(session):
    ...     if session.connection.state is spotify.ConnectionState.LOGGED_IN:
    ...         logged_in_event.set()
    ...
    >>> session = spotify.Session()
    >>> loop = spotify.EventLoop(session)
    >>> loop.start()
    >>> session.on(
    ...     spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    ...     connection_state_listener)
    ...
    >>> session.connection.state
    <ConnectionState.LOGGED_OUT: 0>
    >>> session.login('alice', 's3cretpassword')
    >>> session.connection.state
    <ConnectionState.OFFLINE: 4>
    >>> logged_in_event.wait()
    >>> session.connection.state
    <ConnectionState.LOGGED_IN: 1>
    >>> session.user
    User(u'spotify:user:alice')

Note that when using :class:`~spotify.EventLoop`, your event listener
functions are called from the :class:`~spotify.EventLoop` thread, and not from
your main thread. You may need to add synchronization primitives to protect
your application code from threading issues.


Logging
=======

pyspotify uses Python's standard :mod:`logging` module for logging. All log
records emitted by pyspotify are issued to the logger named ``spotify``, or a
sublogger of it.

Out of the box, pyspotify is set up with :class:`logging.NullHandler` as the
only log record handler. This is the recommended approach for logging in
libraries, so that the application developer using the library will have full
control over how the log records from the library will be exposed to the
application's users. In other words, if you want to see the log records from
pyspotify anywhere, you need to add a useful handler to the root logger or the
logger named ``spotify`` to get any log output from pyspotify. The defaults
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

If we turn on logging, the login process is a bit more informative::

    >>> import logging
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> import spotify
    >>> session = spotify.Session()
    >>> session.login('alice', 's3cretpassword')
    DEBUG:spotify.session:Notify main thread
    DEBUG:spotify.session:Log message from Spotify: 19:15:54.829 I [ap:1752] Connecting to AP ap.spotify.com:4070
    DEBUG:spotify.session:Log message from Spotify: 19:15:54.862 I [ap:1226] Connected to AP: 78.31.12.11:4070
    >>> session.process_events()
    DEBUG:spotify.session:Notify main thread
    DEBUG:spotify.session:Log message from Spotify: 19:17:27.972 E [session:926] Not all tracks cached
    INFO:spotify.session:Logged in
    DEBUG:spotify.session:Credentials blob updated: 'NfFEO...'
    DEBUG:spotify.session:Connection state updated
    43
    >>> session.user
    User(u'spotify:user:alice')


Browsing metadata
=================

When we're logged in, the objects we created from Spotify URIs becomes a lot
more interesting::

    >>> album = session.get_album('spotify:album:0XHpO9qTpqJJQwa2zFxAAE')

If the object isn't loaded, you can call :meth:`~spotify.Album.load` to block
until the object is loaded with data::

    >>> album.is_loaded
    False
    >>> album.name is None
    True
    >>> album.load()
    Album('spotify:album:0XHpO9qTpqJJQwa2zFxAAE')
    >>> album.name
    u'Reach For Glory'
    >>> album.artist
    Artist(u'spotify:artist:4kjWnaLfIRcLJ1Dy4Wr6tY')
    >>> album.artist.load().name
    u'Blackmill'

The :class:`~spotify.Album` object give you the most basic information about
an album. For more metadata, you can call :meth:`~spotify.Album.browse()` to
get an :class:`~spotify.AlbumBrowser`::

    >>> browser = album.browse()

The browser also needs to load data, but once its loaded, most related objects
are in place with data as well::

    >>> browser.load()
    AlbumBrowser(u'spotify:album:0XHpO9qTpqJJQwa2zFxAAE')
    >>> browser.copyrights
    [u'2011 Blackmill']
    >>> browser.tracks
    [Track(u'spotify:track:4FXj4ZKMO2dSkqiAhV7L8t'),
     Track(u'spotify:track:1sYClIlZZsL6dVMVTxCYRm'),
     Track(u'spotify:track:1uY4O332HuqLIcSSJlg4NX'),
     Track(u'spotify:track:58qbTrCRGyjF9tnjvHDqAD'),
     Track(u'spotify:track:3RZzg8yZs5HaRjQiDiBIsV'),
     Track(u'spotify:track:4jIzCryeLdBgE671gdQ6QD'),
     Track(u'spotify:track:4JNpKcFjVFYIzt1D95dmi0'),
     Track(u'spotify:track:7wAtUSgh6wN5ZmuPRRXHyL'),
     Track(u'spotify:track:7HYOVVLd5XnfY4yyV5Neke'),
     Track(u'spotify:track:2YfVXi6dTux0x8KkWeZdd3'),
     Track(u'spotify:track:6HPKugiH3p0pUJBNgUQoou')]
    >>> [(t.index, t.name, t.duration // 1000) for t in browser.tracks]
    [(1, u'Evil Beauty', 228),
     (2, u'City Lights', 299),
     (3, u'A Reach For Glory', 254),
     (4, u'Relentless', 194),
     (5, u'In The Night Of Wilderness', 327),
     (6, u"Journey's End", 296),
     (7, u'Oh Miah', 333),
     (8, u'Flesh and Bones', 276),
     (9, u'Sacred River', 266),
     (10, u'Rain', 359),
     (11, u'As Time Goes By', 97)]


Downloading cover art
=====================

While we're at it, let's do something a bit more impressive; getting cover
art::

    >>> cover = album.cover(spotify.ImageSize.LARGE)
    >>> cover.load()
    Image(u'spotify:image:16eaba4959d5d97e8c0ca04289e0b1baaefae55f')

Currently, all covers are in JPEG format::

    >>> cover.format
    <ImageFormat.JPEG: 0>

The :class:`~spotify.Image` object gives access to the raw JPEG data::

    >>> len(cover.data)
    37204
    >>> cover.data[:20]
    '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'

For convenience, it also provides the same data encoded as a ``data:`` URI for
easy embedding into HTML documents::

    >>> len(cover.data_uri)
    49631
    >>> cover.data_uri[:60]
    u'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCA'

If you're following along, you can try writing the image data out to files and
inspect the result yourself::

    >>> open('/tmp/cover.jpg', 'w+').write(cover.data)
    >>> open('/tmp/cover.html', 'w+').write('<img src="%s">' % cover.data_uri)


Searching
=========

.. warning::

    The search API was broken at 2016-02-03 by a server-side change
    made by Spotify. The functionality was never restored.

    Please use the Spotify Web API to perform searches.

If you don't have the URI to a Spotify object, another way to get started is
to :meth:`~spotify.Session.search`::

    >>> search = session.search('massive attack')
    >>> search.load()
    Search(u'spotify:search:massive+attack')

A search returns lists of matching artists, albums, tracks, and playlists::

    >>> (search.artist_total, search.album_total, search.track_total, track.playlist_total)
    (5, 50, 564, 125)
    >>> search.artists[0].load().name
    u'Massive Attack'
    >>> [a.load().name for a in search.artists[:3]]
    [u'Massive Attack',
     u'Kwanzaa Posse feat. Massive Attack',
     u'Massive Attack Vs. Mad Professor']

Only the first 20 items in each list are returned by default::

    >>> len(search.artists)
    5
    >>> len(search.tracks)
    20

The :class:`~spotify.Search` object can help you with getting
:meth:`~spotify.Search.more` results from the same query::

    >>> search2 = search.more().load()
    >>> len(search2.artists)
    0
    >>> len(search2.tracks)
    20
    >>> search.track_offset
    0
    >>> search.tracks[0]
    Track(u'spotify:track:67Hna13dNDkZvBpTXRIaOJ')
    >>> search2.track_offset
    20
    >>> search2.tracks[0]
    Track(u'spotify:track:3kKVqFF4pv4EXeQe428zl2')

You can also do searches where Spotify tries to figure out what you
mean based on popularity, etc. instead of exact token matches::

    >>> search = session.search('mas').load()
    Search(u'spotify:search:mas')
    >>> search.artists[0].load().name
    u'X-Mas Allstars'

    >>> search = session.search('mas', search_type=spotify.SearchType.SUGGEST).load()
    Search(u'spotify:search:mas')
    >>> search.artists[0].load().name
    u'Massive Attack'


Playlist management
===================

.. warning::

    The playlists API was broken at 2018-05-24 by a server-side change
    made by Spotify. The functionality was never restored.

    Please use the Spotify Web API to work with playlists.

Another way to find some music is to use your Spotify
:class:`~spotify.Playlist`, which can be found in
:attr:`~spotify.Session.playlist_container`::

    >>> len(session.playlist_container)
    53
    >>> playlist = session.playlist_container[0]
    >>> playlist.load()
    Playlist(u'spotify:user:jodal:playlist:5hBcGwxKlnzNnSrREQ4aUe')
    >>> playlist.name
    u'The Glitch Mob - Love Death Immortality'

The :class:`~spotify.PlaylistContainer` object lets you add, remove, move and
rename playlists as well as playlist folders. See the API docs for
:class:`~spotify.PlaylistContainer` for more examples.

::

    >>> del session.playlist_container[0]
    >>> len(session.playlist_container)
    52
    >>> session.playlist_container.insert(0, playlist)
    >>> len(session.playlist_container)
    53

The :class:`~spotify.Playlist` objects let you add, remove and move tracks in
a playlist, as well as turning on things like syncing of the playlist for
offline playback::

    >>> playlist.offline_status
    <PlaylistOfflineStatus.NO: 0>
    >>> playlist.set_offline_mode(True)
    >>> playlist.offline_status
    <PlaylistOfflineStatus.WAITING: 3>
    >>> session.process_events()
    # Probably needed multiple times, before syncing begins
    >>> playlist.offline_status
    <PlaylistOfflineStatus.DOWNLOADING: 2>
    >>> playlist.offline_download_completed
    20
    # More process_events()
    >>> playlist.offline_status
    <PlaylistOfflineStatus.YES: 1>

For more details, see the API docs for :class:`~spotify.Playlist`.


Playing music
=============

Music data is delivered to the :attr:`~spotify.SessionEvent.MUSIC_DELIVERY`
event listener as PCM frames. If you want to have full control of audio
playback, you can deliver these audio frames to your operating systems' audio
subsystem yourself. If you want some help on the road, pyspotify comes with
audio sinks for some select audio subsystems.

For details, have a look at the :class:`spotify.AlsaSink` and
:class:`spotify.PortAudioSink` documentation, and the
``examples/play_track.py`` and ``examples/shell.py`` examples.


Thread safety
=============

If you've read the libspotify documentation, you may have noticed that
libspotify itself isn't thread safe. This means that you must take care to
never call libspotify functions from two threads at the same time, and to
finish your work with any pointers, e.g. strings, returned by libspotify
functions before calling the next libspotify function. In summary, you'll need
to use a single thread for all your use of libspotify, or protect all
libspotify function calls with a single lock.

pyspotify, on the other hand, improves on this so that you can use pyspotify
from multiple threads. pyspotify has a single global lock. This lock is
acquired during all calls to libspotify, for as long as we're working with
pointers returned from libspotify functions, and during all access to
pyspotify's own internal state, like for example the collections of event
listeners. In other words, pyspotify should be safe to use from multiple
threads simultaneously.

Even though pyspotify itself is thread safe, you cannot disregard threading
issues entirely when using pyspotify. There's two things to watch out for.
First, event listeners for a number of the events listed in
:class:`~spotify.SessionEvent` will be called from internal threads in
libspotify itself. This is clearly marked in the documentation for the relevant
events. Second, if you use the :class:`~spotify.EventLoop` helper thread,
listeners for all other events---that is, events *not* emitted from internal
threads in libspotify---will be called from the :class:`~spotify.EventLoop`
thread. This shouldn't be an issue if you just use pyspotify itself from
within the event listeners, but the moment you start working with your
application's state from inside event listeners, you'll need to apply the
proper thread synchronization primitives to avoid getting into trouble.
