from __future__ import unicode_literals

import collections
import pprint
import re

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Playlist',
    'PlaylistContainer',
    'PlaylistFolder',
    'PlaylistOfflineStatus',
    'PlaylistTrack',
    'PlaylistType',
]


class Playlist(object):
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

    def __init__(self, uri=None, sp_playlist=None, add_ref=True):
        assert uri or sp_playlist, 'uri or sp_playlist is required'
        if uri is not None:
            playlist = spotify.Link(uri).as_playlist()
            if playlist is None:
                raise ValueError(
                    'Failed to get playlist from Spotify URI: %r' % uri)
            sp_playlist = playlist._sp_playlist
            add_ref = True
        if add_ref:
            lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

    def __repr__(self):
        if not self.is_loaded:
            return 'Playlist(<not loaded>)'
        try:
            return 'Playlist(%r)' % self.link.uri
        except ValueError as exc:
            return 'Playlist(<error: %s>)' % exc

    @property
    def is_loaded(self):
        """Whether the playlist's data is loaded."""
        return bool(lib.sp_playlist_is_loaded(self._sp_playlist))

    def load(self, timeout=None):
        """Block until the playlist's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    # TODO add_callbacks()
    # TODO remove_callbacks()

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

        lib.sp_playlist_add_ref(self._sp_playlist)
        return utils.Sequence(
            sp_obj=ffi.gc(self._sp_playlist, lib.sp_playlist_release),
            len_func=lib.sp_playlist_num_tracks,
            getitem_func=get_track)

    @property
    def tracks_with_metadata(self):
        """The playlist's tracks with metadata specific to the playlist.

        Will always return an empty list if the search isn't loaded.
        """
        if not self.is_loaded:
            return []

        lib.sp_playlist_add_ref(self._sp_playlist)
        return utils.Sequence(
            sp_obj=ffi.gc(self._sp_playlist, lib.sp_playlist_release),
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

    def is_collaborative(self):
        return bool(lib.sp_playlist_is_collaborative(self._sp_playlist))

    def set_collaborative(self, value):
        spotify.Error.maybe_raise(
            lib.sp_playlist_set_collaborative(self._sp_playlist, int(value)))

    collaborative = property(is_collaborative, set_collaborative)
    """Whether the playlist can be modified by all users or not."""

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

    # TODO reorder_tracks()

    # TODO subscribers collection

    def is_in_ram(self):
        return bool(lib.sp_playlist_is_in_ram(
            spotify.session_instance._sp_session, self._sp_playlist))

    def set_in_ram(self, value):
        spotify.Error.maybe_raise(lib.sp_playlist_set_in_ram(
            spotify.session_instance._sp_session, self._sp_playlist,
            int(value)))

    in_ram = property(is_in_ram, set_in_ram)
    """Whether the playlist is in RAM, and not only on disk.

    A playlist must *currently be* in RAM for tracks to be available. A
    playlist must *have been* in RAM for other metadata to be available.

    By default, playlists are kept in RAM unless
    :attr:`~spotify.SessionConfig.initially_unload_playlists` is set to
    :class:`True` before creating the :class:`~spotify.Session`. If the
    playlists are initially unloaded, set :attr:`in_ram` to :class:`True` to
    have a playlist loaded into RAM.
    """

    def set_offline_mode(self, offline=True):
        """Mark the playlist to be synchronized for offline playback.

        The playlist must be in the current user's playlist container.
        """
        spotify.Error.maybe_raise(lib.sp_playlist_set_offline_mode(
            spotify.session_instance._sp_session, self._sp_playlist,
            int(offline)))

    @property
    def offline_status(self):
        """The playlist's :class:`PlaylistOfflineStatus`.
        """
        # TODO Check behavior when not loaded
        return PlaylistOfflineStatus(lib.sp_playlist_get_offline_status(
            spotify.session_instance._sp_session, self._sp_playlist))

    @property
    def offline_download_completed(self):
        """The download progress for an offline playlist.

        A number in the range 0-100. Always 0 if :attr:`offline_status` isn't
        :attr:`PlaylistOfflineStatus.DOWNLOADING`.
        """
        if self.offline_status != PlaylistOfflineStatus.DOWNLOADING:
            return None
        return int(lib.sp_playlist_get_offline_download_completed(
            spotify.session_instance._sp_session, self._sp_playlist))

    @property
    def link(self):
        """A :class:`Link` to the playlist."""
        return spotify.Link(self)


class PlaylistContainer(collections.Sequence):
    """A Spotify playlist container.

    The playlist container can be accessed as a regular Python collection to
    work with the playlists::

        >>> import spotify
        >>> session = spotify.Session()
        # Login, etc.
        >>> container = session.playlists
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
    """

    def __init__(self, sp_playlistcontainer, add_ref=True):
        if add_ref:
            lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release)

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

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    # TODO add_callbacks()
    # TODO remove_callbacks()

    def __len__(self):
        length = lib.sp_playlistcontainer_num_playlists(
            self._sp_playlistcontainer)
        if length == -1:
            return 0
        return length

    def __getitem__(self, key):
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
            return Playlist(sp_playlist=sp_playlist, add_ref=True)
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
            raise RuntimeError('Unknown playlist type: %r' % playlist_type)

    def add_new_playlist(self, name):
        """Add an empty playlist at the end of the container.

        The playlist name must not be space-only or shorter than 256 chars.

        Returns the new playlist.
        """
        # TODO Add index kwarg and move the playlist if it is specified
        if len(name) > 255:
            raise ValueError('Playlist name must be shorter than 256 chars')
        if len(re.sub('\s+', '', name)) == 0:
            raise ValueError('Playlist name cannot be space-only')
        name = ffi.new('char[]', utils.to_bytes(name))
        sp_playlist = lib.sp_playlistcontainer_add_new_playlist(
            self._sp_playlistcontainer, name)
        if sp_playlist == ffi.NULL:
            raise ValueError('Playlist creation failed')
        return Playlist(sp_playlist=sp_playlist, add_ref=True)

    def add_playlist(self, playlist):
        """Add an existing playlist to the end of the playlist container.

        The playlist can either be a :class:`~spotify.Playlist`, or a
        :class:`~spotify.Link` linking to a playlist.

        Returns the added playlist, or :class:`None` if the playlist already
        existed in the container.
        """
        # TODO Add index kwarg and move the playlist if it is specified
        if isinstance(playlist, spotify.Link):
            link = playlist
        elif isinstance(playlist, spotify.Playlist):
            link = playlist.link
        else:
            raise ValueError(
                'Argument must be Link or Playlist, got %s' % type(playlist))
        sp_playlist = lib.sp_playlistcontainer_add_playlist(
            self._sp_playlistcontainer, link._sp_link)
        if sp_playlist == ffi.NULL:
            return None
        else:
            return Playlist(sp_playlist=sp_playlist, add_ref=True)

    def add_folder(self, name, index=None):
        """Add a playlist folder at the given index.

        If the index isn't specified, the folder is added at the end of the
        container.
        """
        if index is None:
            index = len(self)
        name = ffi.new('char[]', utils.to_bytes(name))
        spotify.Error.maybe_raise(lib.sp_playlistcontainer_add_folder(
            self._sp_playlistcontainer, index, name))

    def remove_playlist(self, index):
        """Remove playlist at the given index from the container."""
        # TODO Make available through __delitem__(index)
        # TODO If removing a PlaylistFolder, make sure to remove the other end
        # of the folder as well
        spotify.Error.maybe_raise(lib.sp_playlistcontainer_remove_playlist(
            self._sp_playlistcontainer, index))

    def move_playlist(self, from_index, to_index, dry_run=False):
        """Move playlist at ``from_index`` to ``to_index``.

        If ``dry_run`` is :class:`True` the move isn't actually done. It is
        only checked if the move is possible.
        """
        spotify.Error.maybe_raise(lib.sp_playlistcontainer_move_playlist(
            self._sp_playlistcontainer, from_index, to_index, int(dry_run)))

    # TODO Add __setitem__, __delitem__, insert, and subclass MutableSequence

    @property
    def owner(self):
        sp_user = lib.sp_playlistcontainer_owner(self._sp_playlistcontainer)
        return spotify.User(sp_user=sp_user)

    # TODO get_unseen_tracks()
    # TODO clear_unseen_tracks()


class PlaylistFolder(collections.namedtuple(
        'PlaylistFolder', ['id', 'name', 'type'])):
    """A playlist folder."""
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
