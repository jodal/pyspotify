from __future__ import unicode_literals

import base64
import logging
import threading

import spotify
from spotify import ffi, lib, serialized, utils

__all__ = ["Image", "ImageFormat", "ImageSize"]

logger = logging.getLogger(__name__)


class Image(object):

    """A Spotify image.

    You can get images from :meth:`Album.cover`, :meth:`Artist.portrait`,
    :meth:`Playlist.image`, or you can create an :class:`Image` yourself from a
    Spotify URI::

        >>> session = spotify.Session()
        # ...
        >>> image = session.get_image(
        ...     'spotify:image:a0bdcbe11b5cd126968e519b5ed1050b0e8183d0')
        >>> image.load().data_uri[:50]
        u'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEBLAEsAAD'

    If ``callback`` isn't :class:`None`, it is expected to be a callable
    that accepts a single argument, an :class:`Image` instance, when
    the image is done loading.
    """

    def __init__(self, session, uri=None, sp_image=None, add_ref=True, callback=None):

        assert uri or sp_image, "uri or sp_image is required"

        self._session = session

        if uri is not None:
            image = spotify.Link(self._session, uri=uri).as_image()
            if image is None:
                raise ValueError("Failed to get image from Spotify URI: %r" % uri)
            sp_image = image._sp_image
            add_ref = True

        if add_ref:
            lib.sp_image_add_ref(sp_image)
        self._sp_image = ffi.gc(sp_image, lib.sp_image_release)

        self.loaded_event = threading.Event()

        handle = ffi.new_handle((self._session, self, callback))
        self._session._callback_handles.add(handle)
        spotify.Error.maybe_raise(
            lib.sp_image_add_load_callback(self._sp_image, _image_load_callback, handle)
        )

    def __repr__(self):
        return "Image(%r)" % self.link.uri

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._sp_image == other._sp_image
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._sp_image)

    loaded_event = None
    """:class:`threading.Event` that is set when the image is loaded."""

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
        return utils.load(self._session, self, timeout=timeout)

    @property
    def format(self):
        """The :class:`ImageFormat` of the image.

        Will always return :class:`None` if the image isn't loaded.
        """
        if not self.is_loaded:
            return None
        return ImageFormat(lib.sp_image_format(self._sp_image))

    @property
    @serialized
    def data(self):
        """The raw image data as a bytestring.

        Will always return :class:`None` if the image isn't loaded.
        """
        if not self.is_loaded:
            return None
        data_size_ptr = ffi.new("size_t *")
        data = lib.sp_image_data(self._sp_image, data_size_ptr)
        buffer_ = ffi.buffer(data, data_size_ptr[0])
        data_bytes = buffer_[:]
        assert len(data_bytes) == data_size_ptr[0], "%r == %r" % (
            len(data_bytes),
            data_size_ptr[0],
        )
        return data_bytes

    @property
    def data_uri(self):
        """The raw image data as a data: URI.

        Will always return :class:`None` if the image isn't loaded.
        """
        if not self.is_loaded:
            return None
        if self.format is not ImageFormat.JPEG:
            raise ValueError("Unknown image format: %r" % self.format)
        return "data:image/jpeg;base64,%s" % (
            base64.b64encode(self.data).decode("ascii")
        )

    @property
    def link(self):
        """A :class:`Link` to the image."""
        return spotify.Link(
            self._session,
            sp_link=lib.sp_link_create_from_image(self._sp_image),
            add_ref=False,
        )


@ffi.callback("void(sp_image *, void *)")
@serialized
def _image_load_callback(sp_image, handle):
    logger.debug("image_load_callback called")
    if handle == ffi.NULL:
        logger.warning("pyspotify image_load_callback called without userdata")
        return
    (session, image, callback) = ffi.from_handle(handle)
    session._callback_handles.remove(handle)
    image.loaded_event.set()
    if callback is not None:
        callback(image)

    # Load callbacks are by nature only called once per image, so we clean up
    # and remove the load callback the first time it is called.
    lib.sp_image_remove_load_callback(sp_image, _image_load_callback, handle)


@utils.make_enum("SP_IMAGE_FORMAT_")
class ImageFormat(utils.IntEnum):
    pass


@utils.make_enum("SP_IMAGE_SIZE_")
class ImageSize(utils.IntEnum):
    pass
