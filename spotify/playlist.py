from __future__ import unicode_literals

import collections
import logging
import pprint
import re

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Playlist',
    'PlaylistEvent',
    'PlaylistContainer',
    'PlaylistContainerEvent',
    'PlaylistFolder',
    'PlaylistOfflineStatus',
    'PlaylistTrack',
    'PlaylistType',
    'PlaylistUnseenTracks',
]

logger = logging.getLogger(__name__)


class Playlist(utils.EventEmitter):
    """A Spotify playlist.

    You can get playlists from the :attr:`~Session.playlist_container`,
    :attr:`~Session.inbox`, :attr:`~Session.starred`,
    :meth:`~Session.starred_for_user`, :meth:`~Session.search`, etc., or you
    can create a playlist yourself from a Spotify URI::

        >>> playlist = spotify.Playlist(
        ...     'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ')
        >>> playlist.load().name
        u'500C feelgood playlist'
    """

    @classmethod
    def _cached(cls, sp_playlist, add_ref=True):
        """
        Get :class:`Playlist` instance for the given ``sp_playlist``. If
        it already exists, it is retrieved from cache.

        Internal method.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized to cache objects')
        if sp_playlist in spotify.session_instance._cache:
            return spotify.session_instance._cache[sp_playlist]
        playlist = Playlist(sp_playlist=sp_playlist, add_ref=add_ref)
        spotify.session_instance._cache[sp_playlist] = playlist
        return playlist

    def __init__(self, uri=None, sp_playlist=None, add_ref=True):
        super(Playlist, self).__init__()

        assert uri or sp_playlist, 'uri or sp_playlist is required'
        if uri is not None:
            playlist = spotify.Link(uri).as_playlist()
            if playlist is None:
                raise spotify.Error(
                    'Failed to get playlist from Spotify URI: %r' % uri)
            sp_playlist = playlist._sp_playlist
            add_ref = True
        if add_ref:
            lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

        self._sp_playlist_callbacks = _PlaylistCallbacks.get_struct()
        lib.sp_playlist_add_callbacks(
            self._sp_playlist, self._sp_playlist_callbacks, ffi.NULL)

    def __del__(self):
        if not hasattr(self, '_sp_playlist'):
            return
        lib.sp_playlist_remove_callbacks(
            self._sp_playlist, self._sp_playlist_callbacks, ffi.NULL)

    def __repr__(self):
        if not self.is_loaded:
            return 'Playlist(<not loaded>)'
        try:
            return 'Playlist(%r)' % self.link.uri
        except spotify.Error as exc:
            return 'Playlist(<error: %s>)' % exc

    @property
    def is_loaded(self):
        """Whether the playlist's data is loaded."""
        return bool(lib.sp_playlist_is_loaded(self._sp_playlist))

    def load(self, timeout=None):
        """Block until the playlist's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self, timeout=timeout)

    @property
    def tracks(self):
        """The playlist's tracks.

        Will always return an empty list if the search isn't loaded.
        """
        if not self.is_loaded:
            return []

        def get_track(sp_playlist, key):
            return spotify.Track(
                sp_track=lib.sp_playlist_track(sp_playlist, key))

        # TODO Negative indexes
        # TODO Adding and removing tracks as if this was a regular list
        return utils.Sequence(
            sp_obj=self._sp_playlist,
            add_ref_func=lib.sp_playlist_add_ref,
            release_func=lib.sp_playlist_release,
            len_func=lib.sp_playlist_num_tracks,
            getitem_func=get_track)

    @property
    def tracks_with_metadata(self):
        """The playlist's tracks, with metadata specific to the playlist as a
        a list of :class:`~spotify.PlaylistTrack` objects.

        Will always return an empty list if the search isn't loaded.
        """
        if not self.is_loaded:
            return []

        return utils.Sequence(
            sp_obj=self._sp_playlist,
            add_ref_func=lib.sp_playlist_add_ref,
            release_func=lib.sp_playlist_release,
            len_func=lib.sp_playlist_num_tracks,
            getitem_func=PlaylistTrack)

    @property
    def name(self):
        """The playlist's name.

        Assigning to :attr:`name` will rename the playlist.

        Will always return :class:`None` if the track isn't loaded.
        """
        name = utils.to_unicode(lib.sp_playlist_name(self._sp_playlist))
        return name if name else None

    @name.setter
    def name(self, new_name):
        self.rename(new_name)

    def rename(self, new_name):
        """Rename the playlist."""
        new_name = ffi.new('char[]', utils.to_bytes(new_name))
        spotify.Error.maybe_raise(
            lib.sp_playlist_rename(self._sp_playlist, new_name))

    @property
    def owner(self):
        """The :class:`User` object for the owner of the playlist."""
        return spotify.User(sp_user=lib.sp_playlist_owner(self._sp_playlist))

    @property
    def collaborative(self):
        """Whether the playlist can be modified by all users or not.

        Set to :class:`True` or :class:`False` to change.
        """
        return bool(lib.sp_playlist_is_collaborative(self._sp_playlist))

    @collaborative.setter
    def collaborative(self, value):
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_collaborative(self._sp_playlist, int(value)))

    def set_autolink_tracks(self, link=True):
        """If a playlist is autolinked, unplayable tracks will be made playable
        by linking them to other Spotify tracks, where possible."""
        # TODO Add a global default setting for if playlists just be autolinked
        # or not. pyspotify 1.x defaults to always autolinking, and doesn't
        # give the user any choice.
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_autolink_tracks(self._sp_playlist, int(link)))

    @property
    def description(self):
        """The playlist's description.

        Will return :class:`None` if the description is unset.
        """
        description = lib.sp_playlist_get_description(self._sp_playlist)
        if description == ffi.NULL:
            return None
        return utils.to_unicode(description)

    @property
    def image(self):
        """The playlist's :class:`Image`.

        Will always return :class:`None` if the playlist isn't loaded or the
        playlist has no image.
        """
        image_id = ffi.new('char[20]')
        has_image = bool(
            lib.sp_playlist_get_image(self._sp_playlist, image_id))
        if not has_image:
            return None
        sp_image = lib.sp_image_create(
            spotify.session_instance._sp_session, image_id)
        return spotify.Image(sp_image=sp_image, add_ref=False)

    @property
    def has_pending_changes(self):
        """Check if the playlist has local changes that has not been
        acknowledged by the server yet.
        """
        return bool(lib.sp_playlist_has_pending_changes(self._sp_playlist))

    def add_tracks(self, tracks, position=None):
        """Add the given tracks to playlist at the given position.

        ``tracks`` can either be a single :class:`~spotify.Track` or a list of
        :class:`~spotify.Track` objects. If ``position`` isn't specified, the
        tracks are added to the end of the playlist.
        """
        if isinstance(tracks, spotify.Track):
            tracks = [tracks]
        if position is None:
            position = len(self.tracks)
        lib.sp_playlist_add_tracks(
            self._sp_playlist, [t._sp_track for t in tracks], len(tracks),
            position, spotify.session_instance._sp_session)

    def remove_tracks(self, tracks):
        """Remove the given tracks from the playlist.

        ``tracks`` can be a single :class:`~spotify.Track` or a list of
        :class:`~spotify.Track` objects.
        """
        if isinstance(tracks, spotify.Track):
            tracks = [tracks]
        tracks = list(set(tracks))  # Remove duplicates
        spotify.Error.maybe_raise(lib.sp_playlist_remove_tracks(
            self._sp_playlist, [t._sp_track for t in tracks], len(tracks)))

    def reorder_tracks(self, tracks, new_position):
        """Move the given ``tracks`` to a ``new_position`` in the playlist.

        ``tracks`` can be a single :class:`~spotify.Track` or a list of
        :class:`~spotify.Track` objects.

        ``new_position`` must be equal to or lower than the current playlist
        length.
        """
        if isinstance(tracks, spotify.Track):
            tracks = [tracks]
        tracks = list(set(tracks))  # Remove duplicates
        spotify.Error.maybe_raise(lib.sp_playlist_reorder_tracks(
            self._sp_playlist, [t._sp_track for t in tracks], len(tracks),
            new_position))

    @property
    def num_subscribers(self):
        """The number of subscribers to the playlist.

        The number can be higher than the length of the :attr:`subscribers`
        collection, especially if the playlist got many subscribers.

        May be zero until you call :meth:`update_subscribers` and the
        :attr:`~PlaylistEvent.SUBSCRIBERS_CHANGED` event is emitted from the
        playlist.
        """
        return lib.sp_playlist_num_subscribers(self._sp_playlist)

    @property
    def subscribers(self):
        """The canonical usernames of up to 500 of the subscribers of the
        playlist.

        May be empty until you call :meth:`update_subscribers` and the
        :attr:`~PlaylistEvent.SUBSCRIBERS_CHANGED` event is emitted from the
        playlist.
        """
        sp_subscribers = ffi.gc(
            lib.sp_playlist_subscribers(self._sp_playlist),
            lib.sp_playlist_subscribers_free)
        # The ``subscribers`` field is ``char *[1]`` according to the struct,
        # so we must cast it to ``char **`` to be able to access more than the
        # first subscriber.
        subscribers = ffi.cast('char **', sp_subscribers.subscribers)
        usernames = []
        for i in range(sp_subscribers.count):
            usernames.append(utils.to_unicode(subscribers[i]))
        return usernames

    def update_subscribers(self):
        """Request an update of :attr:`num_subscribers` and the
        :attr:`subscribers` collection.

        The :attr:`~PlaylistEvent.SUBSCRIBERS_CHANGED` event is emitted from
        the playlist when the subscriber data has been updated.
        """
        spotify.Error.maybe_raise(lib.sp_playlist_update_subscribers(
            spotify.session_instance._sp_session, self._sp_playlist))

    @property
    def is_in_ram(self):
        """Whether the playlist is in RAM, and not only on disk.

        A playlist must *currently be* in RAM for tracks to be available. A
        playlist must *have been* in RAM for other metadata to be available.

        By default, playlists are kept in RAM unless
        :attr:`~spotify.Config.initially_unload_playlists` is set to
        :class:`True` before creating the :class:`~spotify.Session`. If the
        playlists are initially unloaded, use :meth:`set_in_ram` to have a
        playlist loaded into RAM.
        """
        return bool(lib.sp_playlist_is_in_ram(
            spotify.session_instance._sp_session, self._sp_playlist))

    def set_in_ram(self, in_ram=True):
        """Control whether or not to keep the playlist in RAM.

        See :attr:`is_in_ram` for further details.
        """
        spotify.Error.maybe_raise(lib.sp_playlist_set_in_ram(
            spotify.session_instance._sp_session, self._sp_playlist,
            int(in_ram)))

    def set_offline_mode(self, offline=True):
        """Mark the playlist to be synchronized for offline playback.

        The playlist must be in the current user's playlist container.
        """
        spotify.Error.maybe_raise(lib.sp_playlist_set_offline_mode(
            spotify.session_instance._sp_session, self._sp_playlist,
            int(offline)))

    @property
    def offline_status(self):
        """The playlist's :class:`PlaylistOfflineStatus`."""
        return PlaylistOfflineStatus(lib.sp_playlist_get_offline_status(
            spotify.session_instance._sp_session, self._sp_playlist))

    @property
    def offline_download_completed(self):
        """The download progress for an offline playlist.

        A number in the range 0-100. Always :class:`None` if
        :attr:`offline_status` isn't :attr:`PlaylistOfflineStatus.DOWNLOADING`.
        """
        if self.offline_status != PlaylistOfflineStatus.DOWNLOADING:
            return None
        return int(lib.sp_playlist_get_offline_download_completed(
            spotify.session_instance._sp_session, self._sp_playlist))

    @property
    def link(self):
        """A :class:`Link` to the playlist."""
        if not self.is_loaded:
            raise spotify.Error('The playlist must be loaded to create a link')
        sp_link = lib.sp_link_create_from_playlist(self._sp_playlist)
        if sp_link == ffi.NULL:
            if not self.is_in_ram:
                raise spotify.Error(
                    'The playlist must have been in RAM to create a link')
            # TODO Figure out why we can still get NULL here even if
            # the playlist is both loaded and in RAM.
            raise spotify.Error('Failed to get link from Spotify playlist')
        return spotify.Link(sp_link=sp_link, add_ref=False)

    def on(self, event, listener, *user_args):
        if self not in spotify.session_instance._emitters:
            spotify.session_instance._emitters.append(self)
        super(Playlist, self).on(event, listener, *user_args)
    on.__doc__ = utils.EventEmitter.on.__doc__

    def off(self, event=None, listener=None):
        super(Playlist, self).off(event, listener)
        if (self.num_listeners() == 0 and
                self in spotify.session_instance._emitters):
            spotify.session_instance._emitters.remove(self)
    off.__doc__ = utils.EventEmitter.off.__doc__


class PlaylistEvent(object):
    """Playlist events.

    Using :class:`Playlist` objects, you can register listener functions to be
    called when various events occurs in the playlist. This class enumerates
    the available events and the arguments your listener functions will be
    called with.

    Example usage::

        import spotify

        def tracks_added(playlist, tracks, position):
            print('Tracks added to playlist')

        session = spotify.Session()
        # Login, etc...

        playlist = session.playlist_container[0]
        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, tracks_added)

    All events will cause debug log statements to be emitted, even if no
    listeners are registered. Thus, there is no need to register listener
    functions just to log that they're called.
    """

    TRACKS_ADDED = 'tracks_added'
    """Called when one or more tracks have been added to the playlist.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param tracks: the added tracks
    :type tracks: list of :class:`Track`
    :param position: the position in the playlist the tracks were added at
    :type position: int
    """

    TRACKS_REMOVED = 'tracks_removed'
    """Called when one or more tracks have been removed from the playlist.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param tracks: positions of the tracks that were removed
    :type tracks: list of ints
    """

    TRACKS_MOVED = 'tracks_moved'
    """Called when one or more tracks have been moved within a playlist.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param tracks: positions of the tracks that were moved
    :type tracks: list of ints
    :param position: the position in the playlist the tracks were moved to
    :type position: int
    """

    PLAYLIST_RENAMED = 'playlist_renamed'
    """Called when the playlist has been renamed.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """

    PLAYLIST_STATE_CHANGED = 'playlist_state_changed'
    """Called when the state changed for a playlist.

    There are three states that trigger this callback:

    - Collaboration for this playlist has been turned on or off. See
      :meth:`Playlist.is_collaborative`.
    - The playlist started having pending changes, or all pending changes have
      now been committed. See :attr:`Playlist.has_pending_changes`.
    - The playlist started loading, or finished loading. See
      :attr:`Playlist.is_loaded`.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """

    PLAYLIST_UPDATE_IN_PROGRESS = 'playlist_update_in_progress'
    """Called when a playlist is updating or is done updating.

    This is called before and after a series of changes are applied to the
    playlist. It allows e.g. the user interface to defer updating until the
    entire operation is complete.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param done: if the update is completed
    :type done: bool
    """

    PLAYLIST_METADATA_UPDATED = 'playlist_metadata_updated'
    """Called when metadata for one or more tracks in the playlist have been
    updated.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """

    TRACK_CREATED_CHANGED = 'track_created_changed'
    """Called when the create time and/or creator for a playlist entry changes.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param position: the position of the entry in the playlist that was changed
    :type position: int
    :param user: the user that created the playlist entry
    :type user: :class:`User`
    :param time: the time the entry was created, in seconds since Unix epoch
    :type time: int
    """

    TRACK_SEEN_CHANGED = 'track_seen_changed'
    """Called when the seen attribute of a playlist entry changes.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param position: the position of the entry in the playlist that was changed
    :type position: int
    :param seen: wether the entry is seen or not
    :type seen: bool
    """

    DESCRIPTION_CHANGED = 'description_changed'
    """Called when the playlist description has changed.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param description: the new description
    :type description: string
    """

    IMAGE_CHANGED = 'image_changed'
    """Called when the playlist image has changed.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param image: the new image
    :type image: :class:`Image`
    """

    TRACK_MESSAGE_CHANGED = 'track_message_changed'
    """Called when the message attribute of a playlist entry changes.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param position: the position of the entry in the playlist that was changed
    :type position: int
    :param message: the new message
    :type message: string
    """

    SUBSCRIBERS_CHANGED = 'subscribers_changed'
    """Called when playlist subscribers changes, either the count or the
    subscriber names.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """


class _PlaylistCallbacks(object):

    @classmethod
    def get_struct(cls):
        return ffi.new('sp_playlist_callbacks *', {
            'tracks_added': cls.tracks_added,
            'tracks_removed': cls.tracks_removed,
            'tracks_moved': cls.tracks_moved,
            'playlist_renamed': cls.playlist_renamed,
            'playlist_state_changed': cls.playlist_state_changed,
            'playlist_update_in_progress': cls.playlist_update_in_progress,
            'playlist_metadata_updated': cls.playlist_metadata_updated,
            'track_created_changed': cls.track_created_changed,
            'track_seen_changed': cls.track_seen_changed,
            'description_changed': cls.description_changed,
            'image_changed': cls.image_changed,
            'track_message_changed': cls.track_message_changed,
            'subscribers_changed': cls.subscribers_changed,
        })

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, sp_track **tracks, int num_tracks, '
        'int position, void *userdata)')
    def tracks_added(sp_playlist, sp_tracks, num_tracks, position, userdata):
        logger.debug('Tracks added to playlist')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        tracks = [
            spotify.Track(sp_track=sp_tracks[i], add_ref=True)
            for i in range(num_tracks)]
        playlist.emit(
            PlaylistEvent.TRACKS_ADDED, playlist, tracks, int(position))

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, int *tracks, int num_tracks, '
        'void *userdata)')
    def tracks_removed(sp_playlist, tracks, num_tracks, userdata):
        logger.debug('Tracks removed from playlist')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        tracks = [int(tracks[i]) for i in range(num_tracks)]
        playlist.emit(PlaylistEvent.TRACKS_REMOVED, playlist, tracks)

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, int *tracks, int num_tracks, '
        'int position, void *userdata)')
    def tracks_moved(sp_playlist, tracks, num_tracks, position, userdata):
        logger.debug('Tracks moved within playlist')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        tracks = [int(tracks[i]) for i in range(num_tracks)]
        playlist.emit(
            PlaylistEvent.TRACKS_MOVED, playlist, tracks, int(position))

    @staticmethod
    @ffi.callback('void(sp_playlist *playlist, void *userdata)')
    def playlist_renamed(sp_playlist, userdata):
        logger.debug('Playlist renamed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(PlaylistEvent.PLAYLIST_RENAMED, playlist)

    @staticmethod
    @ffi.callback('void(sp_playlist *playlist, void *userdata)')
    def playlist_state_changed(sp_playlist, userdata):
        logger.debug('Playlist state changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(PlaylistEvent.PLAYLIST_STATE_CHANGED, playlist)

    @staticmethod
    @ffi.callback('void(sp_playlist *playlist, bool done, void *userdata)')
    def playlist_update_in_progress(sp_playlist, done, userdata):
        logger.debug('Playlist update in progress')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(
            PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, playlist, bool(done))

    @staticmethod
    @ffi.callback('void(sp_playlist *playlist, void *userdata)')
    def playlist_metadata_updated(sp_playlist, userdata):
        logger.debug('Playlist metadata updated')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(PlaylistEvent.PLAYLIST_METADATA_UPDATED, playlist)

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, int position, sp_user *user, '
        'int when, void *userdata)')
    def track_created_changed(sp_playlist, position, sp_user, when, userdata):
        logger.debug('Playlist track created changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        user = spotify.User(sp_user=sp_user, add_ref=True)
        playlist.emit(
            PlaylistEvent.TRACK_CREATED_CHANGED,
            playlist, int(position), user, int(when))

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, int position, bool seen, void *userdata)')
    def track_seen_changed(sp_playlist, position, seen, userdata):
        logger.debug('Playlist track seen changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(
            PlaylistEvent.TRACK_SEEN_CHANGED,
            playlist, int(position), bool(seen))

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, char *desc, void *userdata)')
    def description_changed(sp_playlist, desc, userdata):
        logger.debug('Playlist description changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(
            PlaylistEvent.DESCRIPTION_CHANGED,
            playlist, utils.to_unicode(desc))

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, byte *image, void *userdata)')
    def image_changed(sp_playlist, image_id, userdata):
        logger.debug('Playlist image changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        sp_image = lib.sp_image_create(
            spotify.session_instance._sp_session, image_id)
        image = spotify.Image(sp_image=sp_image, add_ref=False)
        playlist.emit(PlaylistEvent.IMAGE_CHANGED, playlist, image)

    @staticmethod
    @ffi.callback(
        'void(sp_playlist *playlist, int position, char *message, '
        'void *userdata)')
    def track_message_changed(sp_playlist, position, message, userdata):
        logger.debug('Playlist track message changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(
            PlaylistEvent.TRACK_MESSAGE_CHANGED,
            playlist, int(position), utils.to_unicode(message))

    @staticmethod
    @ffi.callback('void(sp_playlist *playlist, void *userdata)')
    def subscribers_changed(sp_playlist, userdata):
        logger.debug('Playlist subscribers changed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist.emit(PlaylistEvent.SUBSCRIBERS_CHANGED, playlist)


class PlaylistContainer(collections.MutableSequence, utils.EventEmitter):
    """A Spotify playlist container.

    The playlist container can be accessed as a regular Python collection to
    work with the playlists::

        >>> import spotify
        >>> session = spotify.Session()
        # Login, etc.
        >>> container = session.playlist_container
        >>> container.is_loaded
        False
        >>> container.load()
        [Playlist(u'spotify:user:jodal:playlist:6xkJysqhkj9uwufFbUb8sP'),
         Playlist(u'spotify:user:jodal:playlist:0agJjPcOhHnstLIQunJHxo'),
         PlaylistFolder(id=8027491506140518932L, name=u'Shared playlists',
            type=<PlaylistType.START_FOLDER: 1>),
         Playlist(u'spotify:user:p3.no:playlist:7DkMndS2KNVQuf2fOpMt10'),
         PlaylistFolder(id=8027491506140518932L, name=u'',
            type=<PlaylistType.END_FOLDER: 2>)]
        >>> container[0]
        Playlist(u'spotify:user:jodal:playlist:6xkJysqhkj9uwufFbUb8sP')

    As you can see, a playlist container can contain a mix of
    :class:`~spotify.Playlist` and :class:`~spotify.PlaylistFolder` objects.

    The container supports operations that changes the container as well.

    To add a playlist you can use :meth:`append` or :meth:`insert` with either
    the name of a new playlist or an existing playlist object. For example::

        >>> playlist = spotify.Playlist(
        ...     'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ')
        >>> container.insert(3, playlist)
        >>> container.append('New empty playlist')

    To remove a playlist or folder you can use :meth:`remove_playlist`, or::

        >>> del container[0]

    To replace an existing playlist or folder with a new empty playlist with
    the given name you can use :meth:`remove_playlist` and
    :meth:`add_new_playlist`, or::

        >>> container[0] = 'My other new empty playlist'

    To replace an existing playlist or folder with an existing playlist you can
    :use :meth:`remove_playlist` and :meth:`add_playlist`, or::

        >>> container[0] = playlist
    """

    @classmethod
    def _cached(cls, sp_playlistcontainer, add_ref=True):
        """
        Get :class:`PlaylistContainer` instance for the given
        ``sp_playlistcontainer``. If it already exists, it is retrieved from
        cache.

        Internal method.
        """
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized to cache objects')
        if sp_playlistcontainer in spotify.session_instance._cache:
            return spotify.session_instance._cache[sp_playlistcontainer]
        playlist_container = PlaylistContainer(
            sp_playlistcontainer=sp_playlistcontainer, add_ref=add_ref)
        spotify.session_instance._cache[sp_playlistcontainer] = (
            playlist_container)
        return playlist_container

    def __init__(self, sp_playlistcontainer, add_ref=True):
        super(PlaylistContainer, self).__init__()

        if add_ref:
            lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release)

        self._sp_playlistcontainer_callbacks = (
            _PlaylistContainerCallbacks.get_struct())
        lib.sp_playlistcontainer_add_callbacks(
            self._sp_playlistcontainer, self._sp_playlistcontainer_callbacks,
            ffi.NULL)

    def __del__(self):
        lib.sp_playlistcontainer_remove_callbacks(
            self._sp_playlistcontainer, self._sp_playlistcontainer_callbacks,
            ffi.NULL)

    def __repr__(self):
        return '<spotify.PlaylistContainer owned by %s: %s>' % (
            self.owner.link.uri, pprint.pformat(list(self)))

    @property
    def is_loaded(self):
        """Whether the playlist container's data is loaded."""
        return bool(lib.sp_playlistcontainer_is_loaded(
            self._sp_playlistcontainer))

    def load(self, timeout=None):
        """Block until the playlist container's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self, timeout=timeout)

    def __len__(self):
        # Required by collections.Sequence

        length = lib.sp_playlistcontainer_num_playlists(
            self._sp_playlistcontainer)
        if length == -1:
            return 0
        return length

    def __getitem__(self, key):
        # Required by collections.Sequence

        if isinstance(key, slice):
            return list(self).__getitem__(key)
        if not isinstance(key, int):
            raise TypeError(
                'list indices must be int or slice, not %s' %
                key.__class__.__name__)
        if not 0 <= key < self.__len__():
            raise IndexError('list index out of range')

        playlist_type = PlaylistType(lib.sp_playlistcontainer_playlist_type(
            self._sp_playlistcontainer, key))

        if playlist_type is PlaylistType.PLAYLIST:
            sp_playlist = lib.sp_playlistcontainer_playlist(
                self._sp_playlistcontainer, key)
            return Playlist._cached(sp_playlist, add_ref=True)
        elif playlist_type in (
                PlaylistType.START_FOLDER, PlaylistType.END_FOLDER):
            return PlaylistFolder(
                id=lib.sp_playlistcontainer_playlist_folder_id(
                    self._sp_playlistcontainer, key),
                name=utils.get_with_fixed_buffer(
                    100,
                    lib.sp_playlistcontainer_playlist_folder_name,
                    self._sp_playlistcontainer, key),
                type=playlist_type)
        else:
            raise spotify.Error('Unknown playlist type: %r' % playlist_type)

    def __setitem__(self, key, value):
        # Required by collections.MutableSequence

        if not isinstance(key, (int, slice)):
            raise TypeError(
                'list indices must be int or slice, not %s' %
                key.__class__.__name__)
        if isinstance(key, slice):
            if not isinstance(value, collections.Iterable):
                raise TypeError('can only assign an iterable')
        if isinstance(key, int):
            if not 0 <= key < self.__len__():
                raise IndexError('list index out of range')
            key = slice(key, key + 1)
            value = [value]

        # In case playlist creation fails, we create before we remove any
        # playlists.
        for i, val in enumerate(value, key.start):
            if isinstance(val, Playlist):
                self.add_playlist(val, index=i)
            else:
                self.add_new_playlist(val, index=i)

        # Adjust for the new playlist at position key.start.
        key = slice(key.start + len(value), key.stop + len(value), key.step)
        del self[key]

    def __delitem__(self, key):
        # Required by collections.MutableSequence

        if isinstance(key, slice):
            start, stop, step = key.indices(self.__len__())
            indexes = range(start, stop, step)
            for i in reversed(sorted(indexes)):
                self.remove_playlist(i)
            return
        if not isinstance(key, int):
            raise TypeError(
                'list indices must be int or slice, not %s' %
                key.__class__.__name__)
        if not 0 <= key < self.__len__():
            raise IndexError('list index out of range')
        self.remove_playlist(key)

    def add_new_playlist(self, name, index=None):
        """Add an empty playlist with ``name`` at the given ``index``.

        The playlist name must not be space-only or longer than 255 chars.

        If the ``index`` isn't specified, the new playlist is added at the end
        of the container.

        Returns the new playlist.
        """
        self._validate_name(name)
        name = ffi.new('char[]', utils.to_bytes(name))
        sp_playlist = lib.sp_playlistcontainer_add_new_playlist(
            self._sp_playlistcontainer, name)
        if sp_playlist == ffi.NULL:
            raise spotify.Error('Playlist creation failed')
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        if index is not None:
            self.move_playlist(self.__len__() - 1, index)
        return playlist

    def add_playlist(self, playlist, index=None):
        """Add an existing ``playlist`` to the playlist container at the given
        ``index``.

        The playlist can either be a :class:`~spotify.Playlist`, or a
        :class:`~spotify.Link` linking to a playlist.

        If the ``index`` isn't specified, the playlist is added at the end of
        the container.

        Returns the added playlist, or :class:`None` if the playlist already
        existed in the container. If the playlist already exists, it will not
        be moved to the given ``index``.
        """
        if isinstance(playlist, spotify.Link):
            link = playlist
        elif isinstance(playlist, spotify.Playlist):
            link = playlist.link
        else:
            raise TypeError(
                'Argument must be Link or Playlist, got %s' % type(playlist))
        sp_playlist = lib.sp_playlistcontainer_add_playlist(
            self._sp_playlistcontainer, link._sp_link)
        if sp_playlist == ffi.NULL:
            return None
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        if index is not None:
            self.move_playlist(self.__len__() - 1, index)
        return playlist

    def add_folder(self, name, index=None):
        """Add a playlist folder with ``name`` at the given ``index``.

        The playlist folder name must not be space-only or longer than 255
        chars.

        If the ``index`` isn't specified, the folder is added at the end of the
        container.
        """
        self._validate_name(name)
        if index is None:
            index = self.__len__()
        name = ffi.new('char[]', utils.to_bytes(name))
        spotify.Error.maybe_raise(lib.sp_playlistcontainer_add_folder(
            self._sp_playlistcontainer, index, name))

    def _validate_name(self, name):
        if len(name) > 255:
            raise ValueError('Playlist name cannot be longer than 255 chars')
        if len(re.sub('\s+', '', name)) == 0:
            raise ValueError('Playlist name cannot be space-only')

    def remove_playlist(self, index, recursive=False):
        """Remove playlist at the given index from the container.

        If the item at the given ``index`` is the start or the end of a
        playlist folder, and the other end of the folder is found, it is also
        removed. The folder content is kept, but is moved one level up the
        folder hierarchy. If ``recursive`` is :class:`True`, the folder content
        is removed as well.

        Using ``del playlist_container[3]`` is equivalent to
        ``playlist_container.remove_playlist(3)``. Similarly, ``del
        playlist_container[0:2]`` is equivalent to calling this method with
        indexes ``1`` and ``0``.
        """
        item = self[index]
        if isinstance(item, PlaylistFolder):
            indexes = self._find_folder_indexes(self, item.id, recursive)
        else:
            indexes = [index]
        for i in reversed(sorted(indexes)):
            spotify.Error.maybe_raise(
                lib.sp_playlistcontainer_remove_playlist(
                    self._sp_playlistcontainer, i))

    @staticmethod
    def _find_folder_indexes(container, folder_id, recursive):
        indexes = []
        for i, item in enumerate(container):
            if isinstance(item, PlaylistFolder) and item.id == folder_id:
                indexes.append(i)
        assert len(indexes) <= 2, (
            'Found more than 2 items with the same playlist folder ID')
        if recursive and len(indexes) == 2:
            start, end = indexes
            indexes = list(range(start, end + 1))
        return indexes

    def move_playlist(self, from_index, to_index, dry_run=False):
        """Move playlist at ``from_index`` to ``to_index``.

        If ``dry_run`` is :class:`True` the move isn't actually done. It is
        only checked if the move is possible.
        """
        spotify.Error.maybe_raise(lib.sp_playlistcontainer_move_playlist(
            self._sp_playlistcontainer, from_index, to_index, int(dry_run)))

    @property
    def owner(self):
        """The :class:`User` object for the owner of the playlist container."""
        sp_user = lib.sp_playlistcontainer_owner(self._sp_playlistcontainer)
        return spotify.User(sp_user=sp_user)

    def get_unseen_tracks(self, playlist):
        """Get a list of unseen tracks in the given ``playlist``.

        The list is a :class:`PlaylistUnseenTracks` instance.

        The tracks will remain "unseen" until :meth:`clear_unseen_tracks` is
        called on the playlist.
        """
        return PlaylistUnseenTracks(
            self._sp_playlistcontainer, playlist._sp_playlist)

    def clear_unseen_tracks(self, playlist):
        """Clears unseen tracks from the given ``playlist``."""
        result = lib.sp_playlistcontainer_clear_unseen_tracks(
            self._sp_playlistcontainer, playlist._sp_playlist)
        if result == -1:
            raise spotify.Error('Failed clearing unseen tracks')

    def insert(self, index, value):
        # Required by collections.MutableSequence

        self[index:index] = [value]

    def on(self, event, listener, *user_args):
        if self not in spotify.session_instance._emitters:
            spotify.session_instance._emitters.append(self)
        super(PlaylistContainer, self).on(event, listener, *user_args)
    on.__doc__ = utils.EventEmitter.on.__doc__

    def off(self, event=None, listener=None):
        super(PlaylistContainer, self).off(event, listener)
        if (self.num_listeners() == 0 and
                self in spotify.session_instance._emitters):
            spotify.session_instance._emitters.remove(self)
    off.__doc__ = utils.EventEmitter.off.__doc__


class PlaylistContainerEvent(object):
    """Playlist container events.

    Using :class:`PlaylistContainer` objects, you can register listener
    functions to be called when various events occurs in the playlist
    container. This class enumerates the available events and the arguments
    your listener functions will be called with.

    Example usage::

        import spotify

        def container_loaded(playlist_container):
            print('Playlist container loaded')

        session = spotify.Session()
        # Login, etc...

        session.playlist_container.on(
            spotify.PlaylistContainerEvent.CONTAINER_LOADED, container_loaded)

    All events will cause debug log statements to be emitted, even if no
    listeners are registered. Thus, there is no need to register listener
    functions just to log that they're called.
    """

    PLAYLIST_ADDED = 'playlist_added'
    """Called when a playlist is added to the container.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    :param playlist: the added playlist
    :type playlist: :class:`Playlist`
    :param position: the position the playlist was added at
    :type position: int
    """

    PLAYLIST_REMOVED = 'playlist_removed'
    """Called when a playlist is removed from the container.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    :param playlist: the removed playlist
    :type playlist: :class:`Playlist`
    :param position: the position the playlist was removed from
    :type position: int
    """

    PLAYLIST_MOVED = 'playlist_moved'
    """Called when a playlist is moved in the container.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    :param playlist: the moved playlist
    :type playlist: :class:`Playlist`
    :param position: the position the playlist was moved from
    :type position: int
    :param new_position: the position the playlist was moved to
    :type new_position: int
    """

    CONTAINER_LOADED = 'container_loaded'
    """Called when the playlist container is loaded.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    """


class _PlaylistContainerCallbacks(object):
    """Internal class."""

    @classmethod
    def get_struct(cls):
        return ffi.new('sp_playlistcontainer_callbacks *', {
            'playlist_added': cls.playlist_added,
            'playlist_removed': cls.playlist_removed,
            'playlist_moved': cls.playlist_moved,
            'container_loaded': cls.container_loaded,
        })

    @staticmethod
    @ffi.callback(
        'void(sp_playlistcontainer *pc, sp_playlist *playlist, int position, '
        'void *userdata)')
    def playlist_added(sp_playlistcontainer, sp_playlist, position, userdata):
        logger.debug('Playlist added at position %d', position)
        playlist_container = PlaylistContainer._cached(
            sp_playlistcontainer, add_ref=True)
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist_container.emit(
            PlaylistContainerEvent.PLAYLIST_ADDED,
            playlist_container, playlist, position)

    @staticmethod
    @ffi.callback(
        'void(sp_playlistcontainer *pc, sp_playlist *playlist, int position, '
        'void *userdata)')
    def playlist_removed(
            sp_playlistcontainer, sp_playlist, position, userdata):
        logger.debug('Playlist removed at position %d', position)
        playlist_container = PlaylistContainer._cached(
            sp_playlistcontainer, add_ref=True)
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist_container.emit(
            PlaylistContainerEvent.PLAYLIST_REMOVED,
            playlist_container, playlist, position)

    @staticmethod
    @ffi.callback(
        'void(sp_playlistcontainer *pc, sp_playlist *playlist, int position, '
        'int new_position, void *userdata)')
    def playlist_moved(
            sp_playlistcontainer, sp_playlist, position, new_position,
            userdata):
        logger.debug(
            'Playlist moved from position %d to %d', position, new_position)
        playlist_container = PlaylistContainer._cached(
            sp_playlistcontainer, add_ref=True)
        playlist = Playlist._cached(sp_playlist, add_ref=True)
        playlist_container.emit(
            PlaylistContainerEvent.PLAYLIST_MOVED,
            playlist_container, playlist, position, new_position)

    @staticmethod
    @ffi.callback(
        'void(sp_playlistcontainer *pc, void *userdata)')
    def container_loaded(sp_playlistcontainer, userdata):
        logger.debug('Playlist container loaded')
        playlist_container = PlaylistContainer._cached(
            sp_playlistcontainer, add_ref=True)
        playlist_container.emit(
            PlaylistContainerEvent.CONTAINER_LOADED, playlist_container)


class PlaylistFolder(collections.namedtuple(
        'PlaylistFolder', ['id', 'name', 'type'])):
    """An object marking the start or end of a playlist folder."""
    pass


@utils.make_enum('SP_PLAYLIST_OFFLINE_STATUS_')
class PlaylistOfflineStatus(utils.IntEnum):
    pass


class PlaylistTrack(object):
    """A playlist track with metadata specific to the playlist.

    Use :attr:`~spotify.Playlist.tracks_with_metadata` to get a list of
    :class:`PlaylistTrack`.
    """

    def __init__(self, sp_playlist, index):
        lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)
        self._index = index

    # TODO Add useful __repr__

    @property
    def track(self):
        """The :class:`~spotify.Track`."""
        return spotify.Track(
            sp_track=lib.sp_playlist_track(self._sp_playlist, self._index))

    @property
    def create_time(self):
        """When the track was added to the playlist, as seconds since Unix
        epoch.
        """
        return lib.sp_playlist_track_create_time(
            self._sp_playlist, self._index)

    @property
    def creator(self):
        """The :class:`~spotify.User` that added the track to the playlist."""
        return spotify.User(sp_user=lib.sp_playlist_track_creator(
            self._sp_playlist, self._index))

    def is_seen(self):
        return bool(lib.sp_playlist_track_seen(self._sp_playlist, self._index))

    def set_seen(self, value):
        spotify.Error.maybe_raise(lib.sp_playlist_track_set_seen(
            self._sp_playlist, self._index, int(value)))

    seen = property(is_seen, set_seen)
    """Whether the track is marked as seen or not."""

    @property
    def message(self):
        """A message attached to the track. Typically used in the inbox."""
        message = lib.sp_playlist_track_message(self._sp_playlist, self._index)
        if message == ffi.NULL:
            return None
        return utils.to_unicode(message)


@utils.make_enum('SP_PLAYLIST_TYPE_')
class PlaylistType(utils.IntEnum):
    pass


class PlaylistUnseenTracks(collections.Sequence):
    """A list of unseen tracks in a playlist.

    The list may contain items that are :class:`None`.

    Returned by :meth:`PlaylistContainer.get_unseen_tracks`.
    """

    _BATCH_SIZE = 100

    def __init__(self, sp_playlistcontainer, sp_playlist):
        lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release)

        lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

        self._num_tracks = 0
        self._sp_tracks_len = 0
        self._get_more_tracks()

    def _get_more_tracks(self):
        self._sp_tracks_len = min(
            self._num_tracks, self._sp_tracks_len + self._BATCH_SIZE)
        self._sp_tracks = ffi.new('sp_track *[]', self._sp_tracks_len)
        self._num_tracks = lib.sp_playlistcontainer_get_unseen_tracks(
            self._sp_playlistcontainer, self._sp_playlist,
            self._sp_tracks, self._sp_tracks_len)

        if self._num_tracks < 0:
            raise spotify.Error('Failed to get unseen tracks for playlist')

    def __len__(self):
        return self._num_tracks

    def __getitem__(self, key):
        if isinstance(key, slice):
            return list(self).__getitem__(key)
        if not isinstance(key, int):
            raise TypeError(
                'list indices must be int or slice, not %s' %
                key.__class__.__name__)
        if not 0 <= key < self.__len__():
            raise IndexError('list index out of range')
        while key >= self._sp_tracks_len:
            self._get_more_tracks()
        sp_track = self._sp_tracks[key]
        if sp_track == ffi.NULL:
            return None
        return spotify.Track(sp_track=sp_track, add_ref=True)

    def __repr__(self):
        return pprint.pformat(list(self))
