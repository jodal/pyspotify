from __future__ import unicode_literals

from spotify import ErrorType, ffi, lib
from spotify.utils import IntEnum, load, make_enum


__all__ = [
    'Image',
    'ImageSize',
]


class Image(object):
    """A Spotify image.

    You can get images from :meth:`Album.cover`, :meth:`Artist.portrait`, or
    from :meth:`Link.as_image` when the link is of the image type.
    """

    def __init__(self, sp_image, add_ref=True):
        if add_ref:
            lib.sp_image_add_ref(sp_image)
        self.sp_image = ffi.gc(sp_image, lib.sp_image_release)

    @property
    def is_loaded(self):
        """Whether the image's data is loaded."""
        return bool(lib.sp_image_is_loaded(self.sp_image))

    @property
    def error(self):
        """An :class:`ErrorType` associated with the image.

        Check to see if there was problems loading the image.
        """
        return ErrorType(lib.sp_image_error(self.sp_image))

    def load(self, timeout=None):
        """Block until the image's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return load(self, timeout=timeout)

    @property
    def link(self):
        """A :class:`Link` to the image."""
        from spotify.link import Link
        return Link(self)

    # TODO Add sp_image_* methods


@make_enum('SP_IMAGE_SIZE_')
class ImageSize(IntEnum):
    pass
