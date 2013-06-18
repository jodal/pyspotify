from __future__ import unicode_literals

import base64

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Image',
    'ImageFormat',
    'ImageSize',
]


class Image(object):
    """A Spotify image.

    You can get images from :meth:`Album.cover`, :meth:`Artist.portrait`, or
    you can create a :class:`Track` yourself from a Spotify URI::

        >>> image = spotify.Image(
        ... 'spotify:image:a0bdcbe11b5cd126968e519b5ed1050b0e8183d0')
        >>> image.load().data_uri[:50]
        u'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEBLAEsAAD'
    """

    def __init__(self, uri=None, sp_image=None, add_ref=True):
        assert uri or sp_image, 'uri or sp_image is required'
        if uri is not None:
            link = spotify.Link(uri)
            sp_image = lib.sp_image_create_from_link(
                spotify.session_instance._sp_session, link._sp_link)
            add_ref = False
            if sp_image is ffi.NULL:
                raise ValueError(
                    'Failed to get image from Spotify URI: %r' % uri)
        if add_ref:
            lib.sp_image_add_ref(sp_image)
        self._sp_image = ffi.gc(sp_image, lib.sp_image_release)

    # TODO Add load callback support using
    # - sp_image_add_load_callback
    # - sp_image_remove_load_callback

    @property
    def is_loaded(self):
        """Whether the image's data is loaded."""
        return bool(lib.sp_image_is_loaded(self._sp_image))

    @property
    def error(self):
        """An :class:`ErrorType` associated with the image.

        Check to see if there was problems loading the image.
        """
        return spotify.ErrorType(lib.sp_image_error(self._sp_image))

    def load(self, timeout=None):
        """Block until the image's data is loaded.

        :param timeout: seconds before giving up and raising an exception
        :type timeout: float
        :returns: self
        """
        return utils.load(self, timeout=timeout)

    @property
    def format(self):
        """The :class:`ImageFormat` of the image.

        Will always return :class:`None` if the image isn't loaded.
        """
        if not self.is_loaded:
            return None
        return ImageFormat(lib.sp_image_format(self._sp_image))

    @property
    def data(self):
        """The raw image data as a bytestring.

        Will always return :class:`None` if the image isn't loaded.
        """
        if not self.is_loaded:
            return None
        data_size_ptr = ffi.new('size_t *')
        data = lib.sp_image_data(self._sp_image, data_size_ptr)
        buffer_ = ffi.buffer(data, data_size_ptr[0])
        data_bytes = buffer_[:]
        assert len(data_bytes) == data_size_ptr[0], '%r == %r' % (
            len(data_bytes), data_size_ptr[0])
        return data_bytes

    @property
    def data_uri(self):
        """The raw image data as a data: URI.

        Will always return :class:`None` if the image isn't loaded.
        """
        if not self.is_loaded:
            return None
        if self.format is not ImageFormat.JPEG:
            raise ValueError('Unknown image format: %r' % self.format)
        return 'data:image/jpeg;base64,%s' % (
            base64.b64encode(self.data).decode('ascii'))

    @property
    def link(self):
        """A :class:`Link` to the image."""
        from spotify.link import Link
        return Link(self)


@utils.make_enum('SP_IMAGE_FORMAT_')
class ImageFormat(utils.IntEnum):
    pass


@utils.make_enum('SP_IMAGE_SIZE_')
class ImageSize(utils.IntEnum):
    pass