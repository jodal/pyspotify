from __future__ import unicode_literals

import logging
import pprint

import spotify
from spotify import compat, ffi, lib, serialized

__all__ = ["PlaylistUnseenTracks"]

logger = logging.getLogger(__name__)


class PlaylistUnseenTracks(compat.Sequence):

    """A list of unseen tracks in a playlist.

    The list may contain items that are :class:`None`.

    Returned by :meth:`PlaylistContainer.get_unseen_tracks`.
    """

    _BATCH_SIZE = 100

    @serialized
    def __init__(self, session, sp_playlistcontainer, sp_playlist):
        self._session = session

        lib.sp_playlistcontainer_add_ref(sp_playlistcontainer)
        self._sp_playlistcontainer = ffi.gc(
            sp_playlistcontainer, lib.sp_playlistcontainer_release
        )

        lib.sp_playlist_add_ref(sp_playlist)
        self._sp_playlist = ffi.gc(sp_playlist, lib.sp_playlist_release)

        self._num_tracks = 0
        self._sp_tracks_len = 0
        self._get_more_tracks()

    @serialized
    def _get_more_tracks(self):
        self._sp_tracks_len = min(
            self._num_tracks, self._sp_tracks_len + self._BATCH_SIZE
        )
        self._sp_tracks = ffi.new("sp_track *[]", self._sp_tracks_len)
        self._num_tracks = lib.sp_playlistcontainer_get_unseen_tracks(
            self._sp_playlistcontainer,
            self._sp_playlist,
            self._sp_tracks,
            self._sp_tracks_len,
        )

        if self._num_tracks < 0:
            raise spotify.Error("Failed to get unseen tracks for playlist")

    def __len__(self):
        return self._num_tracks

    def __getitem__(self, key):
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
        while key >= self._sp_tracks_len:
            self._get_more_tracks()
        sp_track = self._sp_tracks[key]
        if sp_track == ffi.NULL:
            return None
        return spotify.Track(self._session, sp_track=sp_track, add_ref=True)

    def __repr__(self):
        return "PlaylistUnseenTracks(%s)" % pprint.pformat(list(self))
