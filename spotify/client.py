from pyspotify import session
import threading

class Client(object):
    api_version = session.api_version
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

    def connect(self):
        sess = session.connect(self)
        print "Connect, session is", sess
        self.loop(sess) # returns on disconnect

    def disconnect(self):
        print "DISCONNECTING"
        self.exit_code = 0
        self.awoken.set()

    def loop(self, sess):
        print "Looping session", session
        while self.exit_code < 0:
            print "Processing events"
            self.awoken.clear()
            timeout = sess.process_events()
            print "Blocking for event"
            self.awoken.wait()

    def wake(self, sess):
        print "CLIENT AWAKES"
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

    def music_delivery(self, sess, mformat, frames):
        pass

    def play_token_lost(self, sess):
        pass

    def log_message(self, sess, data):
        pass

    def end_of_track(self, sess):
        pass
