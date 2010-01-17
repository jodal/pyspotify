# $Id$
#
# Copyright 2009 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import spotify
import threading

class SpotifySessionManager(object):

    """ Client for spotify. Inherit from this class to have your callbacks
    called on the appropriate events. Exceptions raised in your callback
    handlers will be silently discarded unless you handle them! """

    api_version = spotify.api_version
    cache_location = 'tmp'
    settings_location = 'tmp'
    application_key = None
    appkey_file = 'spotify_appkey.key'
    user_agent = 'pyspotify-example'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        if self.application_key is None:
            self.application_key = open(self.appkey_file).read()
        self.awoken = threading.Event() # used to block until awoken
        self.timer = None
        self.finished = False

    def connect(self):
        sess = spotify.connect(self)
        self.loop(sess) # returns on disconnect

    def loop(self, sess):
        """ The main loop. This processes events and then either waits for an
        event. The event is either triggered by a timer expiring, or by a
        notification from within the spotify subsystem (it calls the wake
        method below). """
        while not self.finished:
            self.awoken.clear()
            timeout = sess.process_events()
            self.timer = threading.Timer(timeout/1000.0, self.awoken.set)
            self.timer.start()
            self.awoken.wait()

    def terminate(self):
        self.finished = True
        self.wake()

    disconnect = terminate

    def wake(self, sess=None):
        """ This is called by the spotify subsystem to wake up the main loop. """
        if self.timer is not None:
            self.timer.cancel()
        self.awoken.set()

    def logged_in(self, session, error):
        """ Called when the user has successfully logged in. You almost
        certainly want to do something with session.playlist_container() at
        this point. """
        pass

    def logged_out(self, sess):
        pass

    def metadata_updated(self, sess):
        pass

    def connection_error(self, sess, error):
        pass

    def message_to_user(self, sess, message):
        pass

    def notify_main_thread(self, sess):
        pass

    def music_delivery(self, sess, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        pass

    def play_token_lost(self, sess):
        pass

    def log_message(self, sess, data):
        pass

    def end_of_track(self, sess):
        pass
