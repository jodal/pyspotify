import session

class Client(object):
    api_version = _spotify.api_version
    cache_location = 'tmp'
    settings_location = 'tmp'
    application_key = None
    appkey_file = 'spotify_appkey.key'
    user_agent='pyspotify-example'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.application_key = open(self.appkey_file).read()
        
    def run(self):
        session.run(self)

    def logged_in(self, session, error):
        pass

    def logged_out(self, session):
        pass

    def metadata_updated(self, session):
        pass

    def connection_error(self, session, error):
        pass

    def message_to_user(self, session, message):
        pass

    def notify_main_thread(self, session):
        pass

    def music_delivery(self, session, mformat, frames):
        pass

    def play_token_lost(self, session):
        pass

    def log_message(self, session, data):
        pass

    def end_of_track(self, session):
        pass
