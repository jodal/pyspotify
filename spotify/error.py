from __future__ import unicode_literals

from spotify import lib, utils


__all__ = [
    'Error',
    'ErrorType',
    'LibError',
    'Timeout',
]


class Error(Exception):
    """A Spotify error."""

    @classmethod
    def maybe_raise(cls, error_type, ignores=None):
        """Raise an :exc:`Error` unless the ``error_type`` is
        :attr:`ErrorType.OK` or in the ``ignores`` list of error types.

        Internal method.
        """
        ignores = set(ignores or [])
        ignores.add(ErrorType.OK)
        if error_type not in ignores:
            raise LibError(error_type)


@utils.make_enum('SP_ERROR_')
class ErrorType(utils.IntEnum):
    pass


class LibError(Error):
    """A libspotify error."""

    def __init__(self, error_type):
        self.error_type = error_type
        message = utils.to_unicode(lib.sp_error_message(error_type))
        super(Error, self).__init__(message)

    def __eq__(self, other):
        return self.error_type == getattr(other, 'error_type', None)

    def __ne__(self, other):
        return not self.__eq__(other)


for attr in dir(lib):
    if attr.startswith('SP_ERROR_'):
        name = attr.replace('SP_ERROR_', '')
        error_no = getattr(lib, attr)
        setattr(LibError, name, LibError(error_no))


class Timeout(Exception):
    """Exception raised by an operation not completing within the given
    timeout."""

    def __init__(self, timeout):
        message = 'Operation did not complete in %.3fs' % timeout
        super(Timeout, self).__init__(message)
