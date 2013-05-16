from __future__ import unicode_literals

import spotify
from spotify import ffi, lib
from spotify.utils import enum, get_with_growing_buffer, to_bytes


__all__ = [
    'Link',
]


@enum('SP_LINK')
class Link(object):
    def __init__(self, value, offset=None):
        if spotify.session_instance is None:
            raise RuntimeError('Session must be initialized to create links')

        if isinstance(value, spotify.Track):
            if offset is None:
                offset = 0
            sp_link = lib.sp_link_create_from_track(value.sp_track, offset)
        elif isinstance(value, spotify.Album):
            sp_link = lib.sp_link_create_from_album(value.sp_album)
        elif isinstance(value, spotify.Artist):
            sp_link = lib.sp_link_create_from_artist(value.sp_artist)
        elif isinstance(value, spotify.Search):
            sp_link = lib.sp_link_create_from_search(value.sp_search)
        elif isinstance(value, spotify.Playlist):
            sp_link = lib.sp_link_create_from_playlist(value.sp_playlist)
        elif isinstance(value, spotify.User):
            sp_link = lib.sp_link_create_from_user(value.sp_user)
        else:
            sp_link = lib.sp_link_create_from_string(
                ffi.new('char[]', to_bytes(value)))
            if sp_link == ffi.NULL:
                raise ValueError(
                    'Failed to get link from Spotify URI: %s' % value)

        self.sp_link = ffi.gc(sp_link, lib.sp_link_release)

    def __str__(self):
        return get_with_growing_buffer(lib.sp_link_as_string, self.sp_link)

    @property
    def type(self):
        return lib.sp_link_type(self.sp_link)

    def as_track(self, offset=None):
        if offset is not None:
            sp_track = lib.sp_link_as_track_and_offset(self.sp_link, offset)
        else:
            sp_track = lib.sp_link_as_track(self.sp_link)
        if sp_track:
            return spotify.Track(sp_track)

    def as_album(self):
        sp_album = lib.sp_link_as_album(self.sp_link)
        if sp_album:
            return spotify.Album(sp_album)

    def as_artist(self):
        sp_artist = lib.sp_link_as_artist(self.sp_link)
        if sp_artist:
            return spotify.Artist(sp_artist)

    def as_user(self):
        sp_user = lib.sp_link_as_user(self.sp_link)
        if sp_user:
            return spotify.User(sp_user)

    # TODO Add all sp_link_* methods
