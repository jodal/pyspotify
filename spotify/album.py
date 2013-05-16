from __future__ import unicode_literals

from spotify import ffi, lib


__all__ = [
    'Album',
]


class Album(object):
    def __init__(self, sp_album):
        lib.sp_album_add_ref(sp_album)
        self.sp_album = ffi.gc(sp_album, lib.sp_album_release)

    def as_link(self):
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_album_* methods
