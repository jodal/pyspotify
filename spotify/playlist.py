from __future__ import unicode_literals

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Playlist',
    'PlaylistContainer',
    'PlaylistOfflineStatus',
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
        return 'spotify.Playlist(%r)' % self.link.uri

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

    # TODO tracks collection

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
    """

    def set_offline_mode(self, offline=True):
        """Mark the playlist to be synchronized for offline playback.

        The playlist must be in the current user's playlist container.
        """
        spotify.Error.maybe_raise(lib.sp_playlist_set_offline_mode(
            spotify.session_instance._sp_session, self._sp_playlist,
            int(offline)))

    # TODO Add sp_playlist_* methods

    @property
    def link(self):
        """A :class:`Link` to the playlist."""
        return spotify.Link(self)


class PlaylistContainer(object):
    """A Spotify playlist container."""

    def __init__(self, sp_playlistcontainer, add_ref=True):
        if add_ref:
            lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release)

    # TODO Add sp_playlistcontainer_* methods


@utils.make_enum('SP_PLAYLIST_OFFLINE_STATUS_')
class PlaylistOfflineStatus(utils.IntEnum):
    pass
