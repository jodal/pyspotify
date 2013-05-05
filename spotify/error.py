from __future__ import unicode_literals

from spotify import lib
from spotify.utils import enum, to_unicode


__all__ = ['Error']


@enum('SP_ERROR_')
class Error(Exception):
    def __init__(self, error_code):
        self.error_code = error_code
        message = to_unicode(lib.sp_error_message(error_code))
        super(Error, self).__init__(message)

    def __eq__(self, other):
        return self.error_code == other.error_code

    def __ne__(self, other):
        return not self.__eq__(other)
