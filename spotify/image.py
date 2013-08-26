from __future__ import unicode_literals

import base64
import logging
import threading
import uuid

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
    you can create a :class:`Track` yourself from a Spotify URI::

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

    def __repr__(self):
        return 'spotify.Image(%r)' % self.link.uri

    load_event = None
    """:class:`threading.Event` that is set when the image is loaded."""

    def add_load_callback(self, callback):
        """Add callback to be called when the image data has loaded.

        Returns a callback ID that can be used to remove the callback again.

        Callbacks added after the image is loaded is called immediately.
        """
        # FIXME Currently, callbacks added before load doesn't seem to be
        # called at all, while callbacks added after load is called
        # immediately.
        key = utils.to_bytes(uuid.uuid4().hex)
        assert key not in spotify.callback_dict
        # TODO This dict entry will survive forever if the Image object is
        # GC-ed without the callback being removed first. Reorganize so that
        # all callback registrations disappears with the Image object.
        spotify.callback_dict[key] = (callback, self)
        userdata = ffi.new('char[32]', key)
        spotify.Error.maybe_raise(lib.sp_image_add_load_callback(
            self._sp_image, _image_load_callback, userdata))
        return key

    def remove_load_callback(self, callback_id):
        """Remove a callback which was added with :meth:`add_load_callback`."""
        if spotify.callback_dict.pop(callback_id, None) is None:
            raise ValueError('No callback with id %r found' % callback_id)
        userdata = ffi.new('char[32]', callback_id)
        spotify.Error.maybe_raise(lib.sp_image_remove_load_callback(
            self._sp_image, _image_load_callback, userdata))

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
        return spotify.Link(self)


@ffi.callback('void(sp_image *, void *)')
def _image_load_callback(sp_image, userdata):
    logger.debug('image_load_callback called')
    if userdata is ffi.NULL:
        logger.warning('image_load_callback called without userdata')
        return
    key = ffi.string(ffi.cast('char[32]', userdata))
    value = spotify.callback_dict.get(key, None)
    if value is None:
        logger.warning(
            'image_load_callback key %r not in callback_dict: %r',
            key, spotify.callback_dict.keys())
        return
    (callback, image) = value
    if callback is not None:
        callback(image)


@utils.make_enum('SP_IMAGE_FORMAT_')
class ImageFormat(utils.IntEnum):
    pass


@utils.make_enum('SP_IMAGE_SIZE_')
class ImageSize(utils.IntEnum):
    pass
