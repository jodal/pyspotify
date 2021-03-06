from __future__ import unicode_literals

import logging

import spotify
from spotify import compat, ffi, lib, serialized, utils

__all__ = ["Playlist", "PlaylistEvent", "PlaylistOfflineStatus"]

logger = logging.getLogger(__name__)


class Playlist(utils.EventEmitter):

    """A Spotify playlist.

    You can get playlists from the :attr:`~Session.playlist_container`,
    :attr:`~Session.inbox`, :meth:`~Session.get_starred`,
    :meth:`~Session.search`, etc., or you can create a playlist yourself from a
    Spotify URI::

        >>> session = spotify.Session()
        # ...
        >>> playlist = session.get_playlist(
        ...     'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ')
        >>> playlist.load().name
        u'500C feelgood playlist'
    """

    @classmethod
    @serialized
    def _cached(cls, session, sp_playlist, add_ref=True):
        """
        Get :class:`Playlist` instance for the given ``sp_playlist``. If
        it already exists, it is retrieved from cache.

        Internal method.
        """
        if sp_playlist in session._cache:
            return session._cache[sp_playlist]
        playlist = Playlist(session, sp_playlist=sp_playlist, add_ref=add_ref)
        session._cache[sp_playlist] = playlist
        return playlist

    @serialized
    def __init__(self, session, uri=None, sp_playlist=None, add_ref=True):
        super(Playlist, self).__init__()

        assert uri or sp_playlist, "uri or sp_playlist is required"

        self._session = session

        if uri is not None:
            sp_playlist = spotify.Link(self._session, uri)._as_sp_playlist()
            if sp_playlist is None:
                raise spotify.Error("Failed to get playlist from Spotify URI: %r" % uri)
            session._cache[sp_playlist] = self
            add_ref = False

        if add_ref:
            lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

        self._sp_playlist_callbacks = None

        # Make sure we remove callbacks in __del__() using the same lib as we
        # added callbacks with.
        self._lib = lib

    def __del__(self):
        if not hasattr(self, "_lib"):
            return
        if getattr(self, "_sp_playlist_callbacks", None) is None:
            return
        self._lib.sp_playlist_remove_callbacks(
            self._sp_playlist, self._sp_playlist_callbacks, ffi.NULL
        )

    def __repr__(self):
        if not self.is_loaded:
            return "Playlist(<not loaded>)"
        try:
            return "Playlist(%r)" % self.link.uri
        except spotify.Error as exc:
            return "Playlist(<error: %s>)" % exc

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_playlist == other._sp_playlist
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_playlist)

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
        return utils.load(self._session, self, timeout=timeout)

    @property
    @serialized
    def tracks(self):
        """The playlist's tracks.

        Will always return an empty list if the playlist isn't loaded.
        """
        if not self.is_loaded:
            return []

        return _Tracks(self._session, self)

    @property
    @serialized
    def tracks_with_metadata(self):
        """The playlist's tracks, with metadata specific to the playlist as a
        a list of :class:`~spotify.PlaylistTrack` objects.

        Will always return an empty list if the playlist isn't loaded.
        """
        if not self.is_loaded:
            return []

        return _PlaylistTracks(self._session, self)

    @property
    @serialized
    def name(self):
        """The playlist's name.

        Assigning to :attr:`name` will rename the playlist.

        Will always return :class:`None` if the playlist isn't loaded.
        """
        name = utils.to_unicode(lib.sp_playlist_name(self._sp_playlist))
        return name if name else None

    @name.setter
    def name(self, new_name):
        self.rename(new_name)

    def rename(self, new_name):
        """Rename the playlist."""
        spotify.Error.maybe_raise(
            lib.sp_playlist_rename(self._sp_playlist, utils.to_char(new_name))
        )

    @property
    @serialized
    def owner(self):
        """The :class:`User` object for the owner of the playlist."""
        return spotify.User(
            self._session,
            sp_user=lib.sp_playlist_owner(self._sp_playlist),
            add_ref=True,
        )

    @property
    def collaborative(self):
        """Whether the playlist can be modified by all users or not.

        Set to :class:`True` or :class:`False` to change.
        """
        return bool(lib.sp_playlist_is_collaborative(self._sp_playlist))

    @collaborative.setter
    def collaborative(self, value):
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_collaborative(self._sp_playlist, int(value))
        )

    def set_autolink_tracks(self, link=True):
        """If a playlist is autolinked, unplayable tracks will be made playable
        by linking them to other Spotify tracks, where possible."""
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_autolink_tracks(self._sp_playlist, int(link))
        )

    @property
    @serialized
    def description(self):
        """The playlist's description.

        Will return :class:`None` if the description is unset.
        """
        description = lib.sp_playlist_get_description(self._sp_playlist)
        return utils.to_unicode_or_none(description)

    def image(self, callback=None):
        """The playlist's :class:`Image`.

        Due to limitations in libspotify's API you can't specify the
        :class:`ImageSize` of these images.

        If ``callback`` isn't :class:`None`, it is expected to be a callable
        that accepts a single argument, an :class:`Image` instance, when
        the image is done loading.

        Will always return :class:`None` if the playlist isn't loaded or the
        playlist has no image.
        """
        image_id = ffi.new("char[20]")
        has_image = bool(lib.sp_playlist_get_image(self._sp_playlist, image_id))
        if not has_image:
            return None
        sp_image = lib.sp_image_create(self._session._sp_session, image_id)
        return spotify.Image(
            self._session, sp_image=sp_image, add_ref=False, callback=callback
        )

    @property
    def has_pending_changes(self):
        """Check if the playlist has local changes that has not been
        acknowledged by the server yet.
        """
        return bool(lib.sp_playlist_has_pending_changes(self._sp_playlist))

    @serialized
    def add_tracks(self, tracks, index=None):
        """Add the given ``tracks`` to playlist at the given ``index``.

        ``tracks`` can either be a single :class:`~spotify.Track` or a list of
        :class:`~spotify.Track` objects. If ``index`` isn't specified, the
        tracks are added to the end of the playlist.
        """
        if isinstance(tracks, spotify.Track):
            tracks = [tracks]
        if index is None:
            index = len(self.tracks)
        spotify.Error.maybe_raise(
            lib.sp_playlist_add_tracks(
                self._sp_playlist,
                [t._sp_track for t in tracks],
                len(tracks),
                index,
                self._session._sp_session,
            )
        )

    def remove_tracks(self, indexes):
        """Remove the tracks at the given ``indexes`` from the playlist.

        ``indexes`` can be a single index or a list of indexes to remove.
        """
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = list(set(indexes))  # Remove duplicates
        spotify.Error.maybe_raise(
            lib.sp_playlist_remove_tracks(self._sp_playlist, indexes, len(indexes))
        )

    def reorder_tracks(self, indexes, new_index):
        """Move the tracks at the given ``indexes`` to a ``new_index`` in the
        playlist.

        ``indexes`` can be a single index or a list of indexes to move.

        ``new_index`` must be equal to or lower than the current playlist
        length.
        """
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = list(set(indexes))  # Remove duplicates
        spotify.Error.maybe_raise(
            lib.sp_playlist_reorder_tracks(
                self._sp_playlist, indexes, len(indexes), new_index
            )
        )

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
    @serialized
    def subscribers(self):
        """The canonical usernames of up to 500 of the subscribers of the
        playlist.

        May be empty until you call :meth:`update_subscribers` and the
        :attr:`~PlaylistEvent.SUBSCRIBERS_CHANGED` event is emitted from the
        playlist.
        """
        sp_subscribers = ffi.gc(
            lib.sp_playlist_subscribers(self._sp_playlist),
            lib.sp_playlist_subscribers_free,
        )
        # The ``subscribers`` field is ``char *[1]`` according to the struct,
        # so we must cast it to ``char **`` to be able to access more than the
        # first subscriber.
        subscribers = ffi.cast("char **", sp_subscribers.subscribers)
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
        spotify.Error.maybe_raise(
            lib.sp_playlist_update_subscribers(
                self._session._sp_session, self._sp_playlist
            )
        )

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
        return bool(
            lib.sp_playlist_is_in_ram(self._session._sp_session, self._sp_playlist)
        )

    def set_in_ram(self, in_ram=True):
        """Control whether or not to keep the playlist in RAM.

        See :attr:`is_in_ram` for further details.
        """
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_in_ram(
                self._session._sp_session, self._sp_playlist, int(in_ram)
            )
        )

    def set_offline_mode(self, offline=True):
        """Mark the playlist to be synchronized for offline playback.

        The playlist must be in the current user's playlist container.
        """
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_offline_mode(
                self._session._sp_session, self._sp_playlist, int(offline)
            )
        )

    @property
    def offline_status(self):
        """The playlist's :class:`PlaylistOfflineStatus`."""
        return PlaylistOfflineStatus(
            lib.sp_playlist_get_offline_status(
                self._session._sp_session, self._sp_playlist
            )
        )

    @property
    def offline_download_completed(self):
        """The download progress for an offline playlist.

        A number in the range 0-100. Always :class:`None` if
        :attr:`offline_status` isn't :attr:`PlaylistOfflineStatus.DOWNLOADING`.
        """
        if self.offline_status != PlaylistOfflineStatus.DOWNLOADING:
            return None
        return int(
            lib.sp_playlist_get_offline_download_completed(
                self._session._sp_session, self._sp_playlist
            )
        )

    @property
    def link(self):
        """A :class:`Link` to the playlist."""
        if not self.is_loaded:
            raise spotify.Error("The playlist must be loaded to create a link")
        sp_link = lib.sp_link_create_from_playlist(self._sp_playlist)
        if sp_link == ffi.NULL:
            if not self.is_in_ram:
                raise spotify.Error(
                    "The playlist must have been in RAM to create a link"
                )
            # XXX Figure out why we can still get NULL here even if
            # the playlist is both loaded and in RAM.
            raise spotify.Error("Failed to get link from Spotify playlist")
        return spotify.Link(self._session, sp_link=sp_link, add_ref=False)

    @serialized
    def on(self, event, listener, *user_args):
        if self._sp_playlist_callbacks is None:
            self._sp_playlist_callbacks = _PlaylistCallbacks.get_struct()
            lib.sp_playlist_add_callbacks(
                self._sp_playlist, self._sp_playlist_callbacks, ffi.NULL
            )
        if self not in self._session._emitters:
            self._session._emitters.append(self)
        super(Playlist, self).on(event, listener, *user_args)

    on.__doc__ = utils.EventEmitter.on.__doc__

    @serialized
    def off(self, event=None, listener=None):
        super(Playlist, self).off(event, listener)
        if self.num_listeners() == 0 and self in self._session._emitters:
            self._session._emitters.remove(self)

    off.__doc__ = utils.EventEmitter.off.__doc__


class PlaylistEvent(object):

    """Playlist events.

    Using :class:`Playlist` objects, you can register listener functions to be
    called when various events occurs in the playlist. This class enumerates
    the available events and the arguments your listener functions will be
    called with.

    Example usage::

        import spotify

        def tracks_added(playlist, tracks, index):
            print('Tracks added to playlist')

        session = spotify.Session()
        # Login, etc...

        playlist = session.playlist_container[0]
        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, tracks_added)

    All events will cause debug log statements to be emitted, even if no
    listeners are registered. Thus, there is no need to register listener
    functions just to log that they're called.
    """

    TRACKS_ADDED = "tracks_added"
    """Called when one or more tracks have been added to the playlist.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param tracks: the added tracks
    :type tracks: list of :class:`Track`
    :param index: the index in the playlist the tracks were added at
    :type index: int
    """

    TRACKS_REMOVED = "tracks_removed"
    """Called when one or more tracks have been removed from the playlist.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param indexes: indexes of the tracks that were removed
    :type indexes: list of ints
    """

    TRACKS_MOVED = "tracks_moved"
    """Called when one or more tracks have been moved within a playlist.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param old_indexes: old indexes of the tracks that were moved
    :type old_indexes: list of ints
    :param new_index: the new index in the playlist the tracks were moved to
    :type new_index: int
    """

    PLAYLIST_RENAMED = "playlist_renamed"
    """Called when the playlist has been renamed.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """

    PLAYLIST_STATE_CHANGED = "playlist_state_changed"
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

    PLAYLIST_UPDATE_IN_PROGRESS = "playlist_update_in_progress"
    """Called when a playlist is updating or is done updating.

    This is called before and after a series of changes are applied to the
    playlist. It allows e.g. the user interface to defer updating until the
    entire operation is complete.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param done: if the update is completed
    :type done: bool
    """

    PLAYLIST_METADATA_UPDATED = "playlist_metadata_updated"
    """Called when metadata for one or more tracks in the playlist have been
    updated.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """

    TRACK_CREATED_CHANGED = "track_created_changed"
    """Called when the create time and/or creator for a playlist entry changes.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param index: the index of the entry in the playlist that was changed
    :type index: int
    :param user: the user that created the playlist entry
    :type user: :class:`User`
    :param time: the time the entry was created, in seconds since Unix epoch
    :type time: int
    """

    TRACK_SEEN_CHANGED = "track_seen_changed"
    """Called when the seen attribute of a playlist entry changes.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param index: the index of the entry in the playlist that was changed
    :type index: int
    :param seen: whether the entry is seen or not
    :type seen: bool
    """

    DESCRIPTION_CHANGED = "description_changed"
    """Called when the playlist description has changed.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param description: the new description
    :type description: string
    """

    IMAGE_CHANGED = "image_changed"
    """Called when the playlist image has changed.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param image: the new image
    :type image: :class:`Image`
    """

    TRACK_MESSAGE_CHANGED = "track_message_changed"
    """Called when the message attribute of a playlist entry changes.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    :param index: the index of the entry in the playlist that was changed
    :type index: int
    :param message: the new message
    :type message: string
    """

    SUBSCRIBERS_CHANGED = "subscribers_changed"
    """Called when playlist subscribers changes, either the count or the
    subscriber names.

    :param playlist: the playlist
    :type playlist: :class:`Playlist`
    """


class _PlaylistCallbacks(object):
    @classmethod
    def get_struct(cls):
        return ffi.new(
            "sp_playlist_callbacks *",
            {
                "tracks_added": cls.tracks_added,
                "tracks_removed": cls.tracks_removed,
                "tracks_moved": cls.tracks_moved,
                "playlist_renamed": cls.playlist_renamed,
                "playlist_state_changed": cls.playlist_state_changed,
                "playlist_update_in_progress": cls.playlist_update_in_progress,
                "playlist_metadata_updated": cls.playlist_metadata_updated,
                "track_created_changed": cls.track_created_changed,
                "track_seen_changed": cls.track_seen_changed,
                "description_changed": cls.description_changed,
                "image_changed": cls.image_changed,
                "track_message_changed": cls.track_message_changed,
                "subscribers_changed": cls.subscribers_changed,
            },
        )

    # XXX Avoid use of the spotify._session_instance global in the following
    # callbacks.

    @staticmethod
    @ffi.callback(
        "void(sp_playlist *playlist, sp_track **tracks, int num_tracks, "
        "int position, void *userdata)"
    )
    def tracks_added(sp_playlist, sp_tracks, num_tracks, index, userdata):
        logger.debug("Tracks added to playlist")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        tracks = [
            spotify.Track(
                spotify._session_instance, sp_track=sp_tracks[i], add_ref=True
            )
            for i in range(num_tracks)
        ]
        playlist.emit(PlaylistEvent.TRACKS_ADDED, playlist, tracks, int(index))

    @staticmethod
    @ffi.callback(
        "void(sp_playlist *playlist, int *tracks, int num_tracks, " "void *userdata)"
    )
    def tracks_removed(sp_playlist, tracks, num_tracks, userdata):
        logger.debug("Tracks removed from playlist")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        tracks = [int(tracks[i]) for i in range(num_tracks)]
        playlist.emit(PlaylistEvent.TRACKS_REMOVED, playlist, tracks)

    @staticmethod
    @ffi.callback(
        "void(sp_playlist *playlist, int *tracks, int num_tracks, "
        "int position, void *userdata)"
    )
    def tracks_moved(sp_playlist, old_indexes, num_tracks, new_index, userdata):
        logger.debug("Tracks moved within playlist")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        old_indexes = [int(old_indexes[i]) for i in range(num_tracks)]
        playlist.emit(PlaylistEvent.TRACKS_MOVED, playlist, old_indexes, int(new_index))

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, void *userdata)")
    def playlist_renamed(sp_playlist, userdata):
        logger.debug("Playlist renamed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(PlaylistEvent.PLAYLIST_RENAMED, playlist)

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, void *userdata)")
    def playlist_state_changed(sp_playlist, userdata):
        logger.debug("Playlist state changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(PlaylistEvent.PLAYLIST_STATE_CHANGED, playlist)

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, bool done, void *userdata)")
    def playlist_update_in_progress(sp_playlist, done, userdata):
        logger.debug("Playlist update in progress")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, playlist, bool(done))

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, void *userdata)")
    def playlist_metadata_updated(sp_playlist, userdata):
        logger.debug("Playlist metadata updated")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(PlaylistEvent.PLAYLIST_METADATA_UPDATED, playlist)

    @staticmethod
    @ffi.callback(
        "void(sp_playlist *playlist, int position, sp_user *user, "
        "int when, void *userdata)"
    )
    def track_created_changed(sp_playlist, index, sp_user, when, userdata):
        logger.debug("Playlist track created changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        user = spotify.User(spotify._session_instance, sp_user=sp_user, add_ref=True)
        playlist.emit(
            PlaylistEvent.TRACK_CREATED_CHANGED,
            playlist,
            int(index),
            user,
            int(when),
        )

    @staticmethod
    @ffi.callback(
        "void(sp_playlist *playlist, int position, bool seen, void *userdata)"
    )
    def track_seen_changed(sp_playlist, index, seen, userdata):
        logger.debug("Playlist track seen changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(
            PlaylistEvent.TRACK_SEEN_CHANGED, playlist, int(index), bool(seen)
        )

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, char *desc, void *userdata)")
    def description_changed(sp_playlist, desc, userdata):
        logger.debug("Playlist description changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(
            PlaylistEvent.DESCRIPTION_CHANGED, playlist, utils.to_unicode(desc)
        )

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, byte *image, void *userdata)")
    def image_changed(sp_playlist, image_id, userdata):
        logger.debug("Playlist image changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        sp_image = lib.sp_image_create(spotify._session_instance._sp_session, image_id)
        image = spotify.Image(
            spotify._session_instance, sp_image=sp_image, add_ref=False
        )
        playlist.emit(PlaylistEvent.IMAGE_CHANGED, playlist, image)

    @staticmethod
    @ffi.callback(
        "void(sp_playlist *playlist, int position, char *message, " "void *userdata)"
    )
    def track_message_changed(sp_playlist, index, message, userdata):
        logger.debug("Playlist track message changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(
            PlaylistEvent.TRACK_MESSAGE_CHANGED,
            playlist,
            int(index),
            utils.to_unicode(message),
        )

    @staticmethod
    @ffi.callback("void(sp_playlist *playlist, void *userdata)")
    def subscribers_changed(sp_playlist, userdata):
        logger.debug("Playlist subscribers changed")
        playlist = Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist.emit(PlaylistEvent.SUBSCRIBERS_CHANGED, playlist)


@utils.make_enum("SP_PLAYLIST_OFFLINE_STATUS_")
class PlaylistOfflineStatus(utils.IntEnum):
    pass


class _Tracks(utils.Sequence, compat.MutableSequence):
    def __init__(self, session, playlist):
        self._session = session
        self._playlist = playlist
        return super(_Tracks, self).__init__(
            sp_obj=playlist._sp_playlist,
            add_ref_func=lib.sp_playlist_add_ref,
            release_func=lib.sp_playlist_release,
            len_func=lib.sp_playlist_num_tracks,
            getitem_func=self.get_track,
        )

    @serialized
    def get_track(self, sp_playlist, key):
        return spotify.Track(
            self._session,
            sp_track=lib.sp_playlist_track(sp_playlist, key),
            add_ref=True,
        )

    def __setitem__(self, key, value):
        # Required by collections.abc.MutableSequence

        if not isinstance(key, (int, slice)):
            raise TypeError(
                "list indices must be int or slice, not %s" % key.__class__.__name__
            )
        if isinstance(key, slice):
            if not isinstance(value, compat.Iterable):
                raise TypeError("can only assign an iterable")
        if isinstance(key, int):
            if not 0 <= key < self.__len__():
                raise IndexError("list index out of range")
            key = slice(key, key + 1)
            value = [value]

        for i, val in enumerate(value, key.start):
            self._playlist.add_tracks(val, index=i)

        key = slice(key.start + len(value), key.stop + len(value), key.step)
        del self[key]

    def __delitem__(self, key):
        # Required by collections.abc.MutableSequence

        if isinstance(key, slice):
            start, stop, step = key.indices(self.__len__())
            indexes = range(start, stop, step)
            for i in reversed(sorted(indexes)):
                self._playlist.remove_tracks(i)
            return
        if not isinstance(key, int):
            raise TypeError(
                "list indices must be int or slice, not %s" % key.__class__.__name__
            )
        if not 0 <= key < self.__len__():
            raise IndexError("list index out of range")
        self._playlist.remove_tracks(key)

    def insert(self, index, value):
        # Required by collections.abc.MutableSequence

        self[index:index] = [value]


class _PlaylistTracks(_Tracks):
    @serialized
    def get_track(self, sp_playlist, key):
        return spotify.PlaylistTrack(self._session, sp_playlist, key)
