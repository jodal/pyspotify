from __future__ import unicode_literals

from spotify import lib, utils


__all__ = [
    'Error',
    'ErrorType',
]


class Error(Exception):
    """A Spotify error."""

    def __init__(self, error_type):
        self.error_type = error_type
        message = utils.to_unicode(lib.sp_error_message(error_type))
        super(Error, self).__init__(message)

    def __eq__(self, other):
        return self.error_type == other.error_type

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def maybe_raise(cls, error_type, ignores=None):
        """Raise an :exc:`Error` unless the ``error_type`` is
        :attr:`ErrorType.OK` or in the ``ignores`` list of error types.

        Internal method.
        """
        ignores = set(ignores or [])
        ignores.add(ErrorType.OK)
        if error_type not in ignores:
            raise Error(error_type)


for attr in dir(lib):
    if attr.startswith('SP_ERROR_'):
        setattr(
            Error, attr.replace('SP_ERROR_', ''), Error(getattr(lib, attr)))


@utils.make_enum('SP_ERROR_')
class ErrorType(utils.IntEnum):
    pass
