import spotify
import threading

class Client(object):

    """ Client for spotify. Inherit from this class to have your callbacks
    called on the appropriate events. Exceptions raised in your callback
    handlers will be silently discarded unless you handle them! """

    api_version = spotify.api_version
    cache_location = 'tmp'
    settings_location = 'tmp'
    application_key = None
    appkey_file = 'spotify_appkey.key'
    user_agent = 'pyspotify-example'
    exit_code = -1

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.application_key = open(self.appkey_file).read()
        self.awoken = threading.Event() # used to block until awoken
        self.timer = None

    def connect(self):
        sess = spotify.connect(self)
        self.loop(sess) # returns on disconnect

    def disconnect(self):
        self.exit_code = 0
        self.awoken.set()

    def loop(self, sess):
        while self.exit_code < 0:
            print "number of active threads:", threading.active_count()
            print "loop 1"
            self.awoken.clear()
            print "loop 2"
            timeout = sess.process_events()
            print "loop 3",timeout/1000.0
            self.timer = threading.Timer(timeout/1000.0, self.awoken.set)
            print "loop 4"
            self.timer.start()
            print "loop 5"
            self.awoken.wait()
            print "loop 6"

    def wake(self, sess):
        print "wake"
        if self.timer is not None:
            self.timer.cancel()
        self.awoken.set()

    def logged_in(self, session, error):
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
