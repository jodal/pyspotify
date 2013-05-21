from __future__ import unicode_literals

import time

import spotify


class Loadable(object):
    """Common functionality for objects that can be loaded.

    The objects must at least have the :attr:`is_loaded` attribute and may also
    have the :meth:`error` method.
    """

    def load(self):
        """Block until the object's data is loaded."""
        # TODO Timeout if this takes too long
        while not self.is_loaded:
            spotify.session_instance.process_events()
            if hasattr(self, 'error'):
                spotify.Error.maybe_raise(
                    self.error, ignores=[spotify.ErrorType.IS_LOADING])
            time.sleep(0.001)
