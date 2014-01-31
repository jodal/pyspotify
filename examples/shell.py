from __future__ import unicode_literals

import cmd
import logging
import Queue as queue
import threading

import spotify


spotify_queue = queue.Queue()
spotify_logged_in = threading.Event()
spotify_logged_out = threading.Event()
spotify_logged_out.set()


class Commander(cmd.Cmd):

    doc_header = 'Commands'
    prompt = 'spotify> '

    logger = logging.getLogger('commander')

    def __init__(self, spotify_queue):
        cmd.Cmd.__init__(self)
        self.spotify_queue = spotify_queue

    def precmd(self, line):
        if line:
            self.logger.debug('New command: %s', line)
        return line

    def emptyline(self):
        pass

    def do_debug(self, line):
        "Show more logging output"
        print('Logging at DEBUG level')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    def do_info(self, line):
        "Show normal logging output"
        print('Logging at INFO level')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    def do_warning(self, line):
        "Show less logging output"
        print('Logging at WARNING level')
        logger = logging.getLogger()
        logger.setLevel(logging.WARNING)

    def do_EOF(self, line):
        "Exit"
        if spotify_logged_in.is_set():
            print('Logging out...')
            self.spotify_queue.put(('logout',))
            spotify_logged_out.wait()
        print('Exiting...')
        self.spotify_queue.put(('exit',))
        return True

    def do_login(self, line):
        "login <username> <password>"
        username, password = line.split(' ', 1)
        self.spotify_queue.put(('login', username, password))
        spotify_logged_in.wait()

    def do_relogin(self, line):
        "relogin -- login as the previous logged in user"
        self.spotify_queue.put(('relogin',))
        spotify_logged_in.wait()

    def do_forget_me(self, line):
        "forget_me -- forget the previous logged in user"
        self.spotify_queue.put(('forget_me',))

    def do_logout(self, line):
        "logout"
        self.spotify_queue.put(('logout',))
        spotify_logged_out.wait()

    def do_whoami(self, line):
        "whoami"
        self.spotify_queue.put(('whoami',))

    def do_play_uri(self, line):
        "play <spotify track uri>"
        self.spotify_queue.put(('play_uri', line))

    def do_search(self, line):
        "search <query>"
        self.spotify_queue.put(('search', line))


def logged_in(session, error):
    # TODO Handle error situations
    spotify_logged_in.set()
    spotify_logged_out.clear()


def logged_out(session):
    spotify_logged_in.clear()
    spotify_logged_out.set()


def notify_main_thread(session):
    spotify_queue.put(('notify_main_thread',))


class SpotifyLoop(threading.Thread):

    logger = logging.getLogger('loop')

    def __init__(self, spotify_queue):
        super(SpotifyLoop, self).__init__()
        self.spotify_queue = spotify_queue

        self.session = spotify.Session()

        self.session.on(spotify.SessionEvent.LOGGED_IN, logged_in)
        self.session.on(spotify.SessionEvent.LOGGED_OUT, logged_out)
        self.session.on(
            spotify.SessionEvent.NOTIFY_MAIN_THREAD, notify_main_thread)

    def run(self):
        self.logger.debug('Spotify event loop started')
        stop = None
        timeout = 1
        while not stop:
            try:
                message = self.spotify_queue.get(timeout=timeout)
                command, args = message[0], message[1:]
                self.logger.debug('New command: %s%s', command, args)
                action = getattr(self, 'do_%s' % command)
                stop = action(*args)
            except queue.Empty:
                self.logger.debug('Timeout reached; processing events')
                timeout = self.session.process_events() / 1000.0
                self.logger.debug('Waiting %.3fs for next message', timeout)
        self.logger.debug('Spotify event loop stopped')

    def do_notify_main_thread(self):
        self.session.process_events()

    def do_login(self, username, password):
        self.session.login(username, password, remember_me=True)

    def do_relogin(self):
        try:
            self.session.relogin()
        except spotify.Error as e:
            self.logger.error(e)
            spotify_logged_in.set()
            spotify_logged_in.clear()

    def do_forget_me(self):
        self.session.forget_me()

    def do_logout(self):
        self.session.logout()

    def do_exit(self):
        return True

    def do_whoami(self):
        if spotify_logged_in.is_set():
            self.logger.info(
                'I am %s aka %s. You can find me at %s',
                self.session.user.canonical_name,
                self.session.user.display_name,
                self.session.user.link)
        else:
            self.logger.info(
                'I am not logged in, but I may be %s',
                self.session.remembered_user)

    def do_play_uri(self, uri):
        if not spotify_logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return
        try:
            track = spotify.Link(uri).as_track()
            track.load()
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            return
        self.logger.info('Loading track into player')
        self.session.player.load(track)
        self.logger.info('Playing track')
        self.session.player.play()

    def do_search(self, query):
        if not spotify_logged_in.is_set():
            self.logger.warning('You must be logged in to search')
            return
        try:
            result = self.session.search(query)
            result.load()
        except spotify.Error as e:
            self.logger.warning(e)
            return
        self.logger.info(
            '%d tracks, %d albums, %d artists, and %d playlists found.',
            result.track_total, result.album_total,
            result.artist_total, result.playlist_total)
        self.logger.info('Top tracks:')
        for track in result.tracks:
            self.logger.info(
                '[%s] %s - %s', track.link, track.artists[0].name, track.name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    spotify_loop = SpotifyLoop(spotify_queue)
    spotify_loop.start()

    Commander(spotify_queue).cmdloop()

    spotify_loop.join()
