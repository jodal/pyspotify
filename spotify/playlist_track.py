from __future__ import unicode_literals

import logging

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["PlaylistTrack"]

logger = logging.getLogger(__name__)


class PlaylistTrack(object):

    """A playlist track with metadata specific to the playlist.

    Use :attr:`~spotify.Playlist.tracks_with_metadata` to get a list of
    :class:`PlaylistTrack`.
    """

    def __init__(self, session, sp_playlist, index):
        self._session = session

        lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

        self._index = index

    def __repr__(self):
        return "PlaylistTrack(uri=%r, creator=%r, create_time=%d)" % (
            self.track.link.uri,
            self.creator,
            self.create_time,
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self._sp_playlist == other._sp_playlist and self._index == other._index
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._sp_playlist, self._index))

    @property
    @serialized
    def track(self):
        """The :class:`~spotify.Track`."""
        return spotify.Track(
            self._session,
            sp_track=lib.sp_playlist_track(self._sp_playlist, self._index),
            add_ref=True,
        )

    @property
    def create_time(self):
        """When the track was added to the playlist, as seconds since Unix
        epoch.
        """
        return lib.sp_playlist_track_create_time(self._sp_playlist, self._index)

    @property
    @serialized
    def creator(self):
        """The :class:`~spotify.User` that added the track to the playlist."""
        return spotify.User(
            self._session,
            sp_user=lib.sp_playlist_track_creator(self._sp_playlist, self._index),
            add_ref=True,
        )

    def is_seen(self):
        return bool(lib.sp_playlist_track_seen(self._sp_playlist, self._index))

    def set_seen(self, value):
        spotify.Error.maybe_raise(
            lib.sp_playlist_track_set_seen(self._sp_playlist, self._index, int(value))
        )

    seen = property(is_seen, set_seen)
    """Whether the track is marked as seen or not."""

    @property
    @serialized
    def message(self):
        """A message attached to the track. Typically used in the inbox."""
        message = lib.sp_playlist_track_message(self._sp_playlist, self._index)
        return utils.to_unicode_or_none(message)
