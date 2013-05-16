from __future__ import unicode_literals

from spotify import ffi, lib
from spotify.utils import enum


__all__ = [
    'Image',
    'ImageSize',
]


class Image(object):
    def __init__(self, sp_image):
        lib.sp_image_add_ref(sp_image)
        self.sp_image = ffi.gc(sp_image, lib.sp_image_release)

    def as_link(self):
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_image_* methods


@enum('SP_IMAGE_SIZE_')
class ImageSize(object):
    pass
