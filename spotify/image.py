from __future__ import unicode_literals

import base64
import logging
import threading

import spotify
from spotify import ffi, lib, utils


__all__ = [
    'Image',
    'ImageFormat',
    'ImageSize',
]

logger = logging.getLogger(__name__)


class Image(object):
    """A Spotify image.

    You can get images from :meth:`Album.cover`, :meth:`Artist.portrait`, or
    you can create an :class:`Image` yourself from a Spotify URI::

        >>> image = spotify.Image(
        ... 'spotify:image:a0bdcbe11b5cd126968e519b5ed1050b0e8183d0')
        >>> image.load().data_uri[:50]
        u'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEBLAEsAAD'
    """

    def __init__(self, uri=None, sp_image=None, add_ref=True):
        assert uri or sp_image, 'uri or sp_image is required'
        if uri is not None:
            image = spotify.Link(uri).as_image()
            if image is None:
                raise ValueError(
                    'Failed to get image from Spotify URI: %r' % uri)
            sp_image = image._sp_image
            add_ref = True
        if add_ref:
            lib.sp_image_add_ref(sp_image)
        self._sp_image = ffi.gc(sp_image, lib.sp_image_release)
        self.load_event = threading.Event()
        self._callback_handles = set()

    def __repr__(self):
        return 'Image(%r)' % self.link.uri

    load_event = None
    """:class:`threading.Event` that is set when the image is loaded."""

    def add_load_callback(self, callback):
        """Add callback to be called when the image data has loaded.

        Returns a callback handle that can be used to remove the callback
        again.

        Callbacks added after the image is loaded is called immediately.
        """
        # FIXME Currently, callbacks added before load doesn't seem to be
        # called at all, while callbacks added after load is called
        # immediately.
        handle = ffi.new_handle((callback, self))
        # TODO Think through the life cycle of the handle object. Can it happen
        # that we GC the image and handle object, and then later the callback
        # is called?
        self._callback_handles.add(handle)
        spotify.Error.maybe_raise(lib.sp_image_add_load_callback(
            self._sp_image, _image_load_callback, handle))
        return handle

    def remove_load_callback(self, handle):
        """Remove a callback which was added with :meth:`add_load_callback`."""
        self._callback_handles.remove(handle)
        spotify.Error.maybe_raise(lib.sp_image_remove_load_callback(
            self._sp_image, _image_load_callback, handle))

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

        After ``timeout`` seconds with no results :exc:`~spotify.Timeout` is
        raised. If ``timeout`` is :class:`None` the default timeout is used.

        The method returns ``self`` to allow for chaining of calls.
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
        return spotify.Link(
            sp_link=lib.sp_link_create_from_image(self._sp_image))


@ffi.callback('void(sp_image *, void *)')
def _image_load_callback(sp_image, handle):
    logger.debug('image_load_callback called')
    if handle == ffi.NULL:
        logger.warning('image_load_callback called without userdata')
        return
    (callback, image) = ffi.from_handle(handle)
    image._callback_handles.remove(handle)
    if callback is not None:
        callback(image)


@utils.make_enum('SP_IMAGE_FORMAT_')
class ImageFormat(utils.IntEnum):
    pass


@utils.make_enum('SP_IMAGE_SIZE_')
class ImageSize(utils.IntEnum):
    pass
