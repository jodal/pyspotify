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
