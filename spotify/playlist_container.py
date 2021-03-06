from __future__ import unicode_literals

import collections
import logging
import pprint
import re

import spotify
from spotify import compat, ffi, lib, serialized, utils

__all__ = [
    "PlaylistContainer",
    "PlaylistContainerEvent",
    "PlaylistFolder",
    "PlaylistPlaceholder",
    "PlaylistType",
]

logger = logging.getLogger(__name__)


class PlaylistContainer(compat.MutableSequence, utils.EventEmitter):

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

        >>> playlist = session.get_playlist(
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
    @serialized
    def _cached(cls, session, sp_playlistcontainer, add_ref=True):
        """
        Get :class:`PlaylistContainer` instance for the given
        ``sp_playlistcontainer``. If it already exists, it is retrieved from
        cache.

        Internal method.
        """
        if sp_playlistcontainer in session._cache:
            return session._cache[sp_playlistcontainer]
        playlist_container = PlaylistContainer(
            session, sp_playlistcontainer=sp_playlistcontainer, add_ref=add_ref
        )
        session._cache[sp_playlistcontainer] = playlist_container
        return playlist_container

    def __init__(self, session, sp_playlistcontainer, add_ref=True):
        super(PlaylistContainer, self).__init__()

        self._session = session

        if add_ref:
            lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release
        )

        self._sp_playlistcontainer_callbacks = None

        # Make sure we remove callbacks in __del__() using the same lib as we
        # added callbacks with.
        self._lib = lib

    def __del__(self):
        if not hasattr(self, "_lib"):
            return
        if getattr(self, "_sp_playlistcontainer_callbacks", None) is None:
            return
        self._lib.sp_playlistcontainer_remove_callbacks(
            self._sp_playlistcontainer,
            self._sp_playlistcontainer_callbacks,
            ffi.NULL,
        )

    def __repr__(self):
        return "PlaylistContainer(%s)" % pprint.pformat(list(self))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_playlistcontainer == other._sp_playlistcontainer
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_playlistcontainer)

    @property
    def is_loaded(self):
        """Whether the playlist container's data is loaded."""
        return bool(lib.sp_playlistcontainer_is_loaded(self._sp_playlistcontainer))

    def load(self, timeout=None):
        """Block until the playlist container's data is loaded.

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
        """
        return utils.load(self._session, self, timeout=timeout)

    def __len__(self):
        # Required by collections.abc.Sequence

        length = lib.sp_playlistcontainer_num_playlists(self._sp_playlistcontainer)
        if length == -1:
            return 0
        return length

    @serialized
    def __getitem__(self, key):
        # Required by collections.abc.Sequence

        if isinstance(key, slice):
            return list(self).__getitem__(key)
        if not isinstance(key, int):
            raise TypeError(
                "list indices must be int or slice, not %s" % key.__class__.__name__
            )
        if key < 0:
            key += self.__len__()
        if not 0 <= key < self.__len__():
            raise IndexError("list index out of range")

        playlist_type = PlaylistType(
            lib.sp_playlistcontainer_playlist_type(self._sp_playlistcontainer, key)
        )

        if playlist_type is PlaylistType.PLAYLIST:
            sp_playlist = lib.sp_playlistcontainer_playlist(
                self._sp_playlistcontainer, key
            )
            return spotify.Playlist._cached(self._session, sp_playlist, add_ref=True)
        elif playlist_type in (
            PlaylistType.START_FOLDER,
            PlaylistType.END_FOLDER,
        ):
            return PlaylistFolder(
                id=lib.sp_playlistcontainer_playlist_folder_id(
                    self._sp_playlistcontainer, key
                ),
                name=utils.get_with_fixed_buffer(
                    100,
                    lib.sp_playlistcontainer_playlist_folder_name,
                    self._sp_playlistcontainer,
                    key,
                ),
                type=playlist_type,
            )
        elif playlist_type is PlaylistType.PLACEHOLDER:
            return PlaylistPlaceholder()
        else:
            raise spotify.Error("Unknown playlist type: %r" % playlist_type)

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

        # In case playlist creation fails, we create before we remove any
        # playlists.
        for i, val in enumerate(value, key.start):
            if isinstance(val, spotify.Playlist):
                self.add_playlist(val, index=i)
            else:
                self.add_new_playlist(val, index=i)

        # Adjust for the new playlist at index key.start.
        key = slice(key.start + len(value), key.stop + len(value), key.step)
        del self[key]

    def __delitem__(self, key):
        # Required by collections.abc.MutableSequence

        if isinstance(key, slice):
            start, stop, step = key.indices(self.__len__())
            indexes = range(start, stop, step)
            for i in reversed(sorted(indexes)):
                self.remove_playlist(i)
            return
        if not isinstance(key, int):
            raise TypeError(
                "list indices must be int or slice, not %s" % key.__class__.__name__
            )
        if not 0 <= key < self.__len__():
            raise IndexError("list index out of range")
        self.remove_playlist(key)

    @serialized
    def add_new_playlist(self, name, index=None):
        """Add an empty playlist with ``name`` at the given ``index``.

        The playlist name must not be space-only or longer than 255 chars.

        If the ``index`` isn't specified, the new playlist is added at the end
        of the container.

        Returns the new playlist.
        """
        self._validate_name(name)
        sp_playlist = lib.sp_playlistcontainer_add_new_playlist(
            self._sp_playlistcontainer, utils.to_char(name)
        )
        if sp_playlist == ffi.NULL:
            raise spotify.Error("Playlist creation failed")
        playlist = spotify.Playlist._cached(self._session, sp_playlist, add_ref=True)
        if index is not None:
            self.move_playlist(self.__len__() - 1, index)
        return playlist

    @serialized
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
                "Argument must be Link or Playlist, got %s" % type(playlist)
            )
        sp_playlist = lib.sp_playlistcontainer_add_playlist(
            self._sp_playlistcontainer, link._sp_link
        )
        if sp_playlist == ffi.NULL:
            return None
        playlist = spotify.Playlist._cached(self._session, sp_playlist, add_ref=True)
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
        spotify.Error.maybe_raise(
            lib.sp_playlistcontainer_add_folder(
                self._sp_playlistcontainer, index, utils.to_char(name)
            )
        )

    def _validate_name(self, name):
        if len(name) > 255:
            raise ValueError("Playlist name cannot be longer than 255 chars")
        if len(re.sub(r"\s+", "", name)) == 0:
            raise ValueError("Playlist name cannot be space-only")

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
                lib.sp_playlistcontainer_remove_playlist(self._sp_playlistcontainer, i)
            )

    @staticmethod
    def _find_folder_indexes(container, folder_id, recursive):
        indexes = []
        for i, item in enumerate(container):
            if isinstance(item, PlaylistFolder) and item.id == folder_id:
                indexes.append(i)
        assert (
            len(indexes) <= 2
        ), "Found more than 2 items with the same playlist folder ID"
        if recursive and len(indexes) == 2:
            start, end = indexes
            indexes = list(range(start, end + 1))
        return indexes

    def move_playlist(self, from_index, to_index, dry_run=False):
        """Move playlist at ``from_index`` to ``to_index``.

        If ``dry_run`` is :class:`True` the move isn't actually done. It is
        only checked if the move is possible.
        """
        if from_index == to_index:
            return
        spotify.Error.maybe_raise(
            lib.sp_playlistcontainer_move_playlist(
                self._sp_playlistcontainer, from_index, to_index, int(dry_run)
            )
        )

    @property
    @serialized
    def owner(self):
        """The :class:`User` object for the owner of the playlist container."""
        return spotify.User(
            self._session,
            sp_user=lib.sp_playlistcontainer_owner(self._sp_playlistcontainer),
            add_ref=True,
        )

    def get_unseen_tracks(self, playlist):
        """Get a list of unseen tracks in the given ``playlist``.

        The list is a :class:`PlaylistUnseenTracks` instance.

        The tracks will remain "unseen" until :meth:`clear_unseen_tracks` is
        called on the playlist.
        """
        return spotify.PlaylistUnseenTracks(
            self._session, self._sp_playlistcontainer, playlist._sp_playlist
        )

    def clear_unseen_tracks(self, playlist):
        """Clears unseen tracks from the given ``playlist``."""
        result = lib.sp_playlistcontainer_clear_unseen_tracks(
            self._sp_playlistcontainer, playlist._sp_playlist
        )
        if result == -1:
            raise spotify.Error("Failed clearing unseen tracks")

    def insert(self, index, value):
        # Required by collections.abc.MutableSequence

        self[index:index] = [value]

    @serialized
    def on(self, event, listener, *user_args):
        if self._sp_playlistcontainer_callbacks is None:
            self._sp_playlistcontainer_callbacks = (
                _PlaylistContainerCallbacks.get_struct()
            )
            lib.sp_playlistcontainer_add_callbacks(
                self._sp_playlistcontainer,
                self._sp_playlistcontainer_callbacks,
                ffi.NULL,
            )
        if self not in self._session._emitters:
            self._session._emitters.append(self)
        super(PlaylistContainer, self).on(event, listener, *user_args)

    on.__doc__ = utils.EventEmitter.on.__doc__

    @serialized
    def off(self, event=None, listener=None):
        super(PlaylistContainer, self).off(event, listener)
        if self.num_listeners() == 0 and self in self._session._emitters:
            self._session._emitters.remove(self)

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

    PLAYLIST_ADDED = "playlist_added"
    """Called when a playlist is added to the container.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    :param playlist: the added playlist
    :type playlist: :class:`Playlist`
    :param index: the index the playlist was added at
    :type index: int
    """

    PLAYLIST_REMOVED = "playlist_removed"
    """Called when a playlist is removed from the container.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    :param playlist: the removed playlist
    :type playlist: :class:`Playlist`
    :param index: the index the playlist was removed from
    :type index: int
    """

    PLAYLIST_MOVED = "playlist_moved"
    """Called when a playlist is moved in the container.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    :param playlist: the moved playlist
    :type playlist: :class:`Playlist`
    :param old_index: the index the playlist was moved from
    :type old_index: int
    :param new_index: the index the playlist was moved to
    :type new_index: int
    """

    CONTAINER_LOADED = "container_loaded"
    """Called when the playlist container is loaded.

    :param playlist_container: the playlist container
    :type playlist_container: :class:`PlaylistContainer`
    """


class _PlaylistContainerCallbacks(object):

    """Internal class."""

    @classmethod
    def get_struct(cls):
        return ffi.new(
            "sp_playlistcontainer_callbacks *",
            {
                "playlist_added": cls.playlist_added,
                "playlist_removed": cls.playlist_removed,
                "playlist_moved": cls.playlist_moved,
                "container_loaded": cls.container_loaded,
            },
        )

    # XXX Avoid use of the spotify._session_instance global in the following
    # callbacks.

    @staticmethod
    @ffi.callback(
        "void(sp_playlistcontainer *pc, sp_playlist *playlist, int position, "
        "void *userdata)"
    )
    def playlist_added(sp_playlistcontainer, sp_playlist, index, userdata):
        logger.debug("Playlist added at index %d", index)
        playlist_container = PlaylistContainer._cached(
            spotify._session_instance, sp_playlistcontainer, add_ref=True
        )
        playlist = spotify.Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist_container.emit(
            PlaylistContainerEvent.PLAYLIST_ADDED,
            playlist_container,
            playlist,
            index,
        )

    @staticmethod
    @ffi.callback(
        "void(sp_playlistcontainer *pc, sp_playlist *playlist, int position, "
        "void *userdata)"
    )
    def playlist_removed(sp_playlistcontainer, sp_playlist, index, userdata):
        logger.debug("Playlist removed at index %d", index)
        playlist_container = PlaylistContainer._cached(
            spotify._session_instance, sp_playlistcontainer, add_ref=True
        )
        playlist = spotify.Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist_container.emit(
            PlaylistContainerEvent.PLAYLIST_REMOVED,
            playlist_container,
            playlist,
            index,
        )

    @staticmethod
    @ffi.callback(
        "void(sp_playlistcontainer *pc, sp_playlist *playlist, int position, "
        "int new_position, void *userdata)"
    )
    def playlist_moved(
        sp_playlistcontainer, sp_playlist, old_index, new_index, userdata
    ):
        logger.debug("Playlist moved from index %d to %d", old_index, new_index)
        playlist_container = PlaylistContainer._cached(
            spotify._session_instance, sp_playlistcontainer, add_ref=True
        )
        playlist = spotify.Playlist._cached(
            spotify._session_instance, sp_playlist, add_ref=True
        )
        playlist_container.emit(
            PlaylistContainerEvent.PLAYLIST_MOVED,
            playlist_container,
            playlist,
            old_index,
            new_index,
        )

    @staticmethod
    @ffi.callback("void(sp_playlistcontainer *pc, void *userdata)")
    def container_loaded(sp_playlistcontainer, userdata):
        logger.debug("Playlist container loaded")
        playlist_container = PlaylistContainer._cached(
            spotify._session_instance, sp_playlistcontainer, add_ref=True
        )
        playlist_container.emit(
            PlaylistContainerEvent.CONTAINER_LOADED, playlist_container
        )


class PlaylistFolder(collections.namedtuple("PlaylistFolder", ["id", "name", "type"])):

    """An object marking the start or end of a playlist folder."""

    pass


class PlaylistPlaceholder(object):
    """An object marking an unknown entry in the playlist container."""

    pass


@utils.make_enum("SP_PLAYLIST_TYPE_")
class PlaylistType(utils.IntEnum):
    pass
