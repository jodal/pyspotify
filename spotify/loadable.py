from __future__ import unicode_literals

import time

import spotify


class Loadable(object):
    """Common functionality for objects that can be loaded.

    The objects must at least have the :attr:`is_loaded` attribute and may also
    have the :meth:`error` method.
    """

    def load(self):
        # TODO Timeout if this takes too long
        while not self.is_loaded:
            spotify.session_instance.process_events()
            if hasattr(self, 'error'):
                if self.error() not in (
                        spotify.Error.OK, spotify.Error.IS_LOADING):
                    raise self.error()
            time.sleep(0.001)
