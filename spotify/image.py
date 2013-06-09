from __future__ import unicode_literals

from spotify import ffi, lib
from spotify.utils import IntEnum, make_enum


__all__ = [
    'Image',
    'ImageSize',
]


class Image(object):
    """A Spotify image."""

    def __init__(self, sp_image):
        lib.sp_image_add_ref(sp_image)
        self.sp_image = ffi.gc(sp_image, lib.sp_image_release)

    @property
    def link(self):
        """A :class:`Link` to the search."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_image_* methods


@make_enum('SP_IMAGE_SIZE_')
class ImageSize(IntEnum):
    pass
