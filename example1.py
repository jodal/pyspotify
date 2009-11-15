#!/usr/bin/env python

import sys
import traceback
import time

from spotify.manager import SpotifySessionManager
from spotify.alsahelper import AlsaController

class Example1(SpotifySessionManager):

    queued = False
    playlist = 2
    track = 0

    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.audio = AlsaController()

    def logged_in(self, session, error):
        print "logged_in"
        try:
            self.ctr = session.playlist_container()
            print "Got playlist container", repr(self.ctr)
        except:
            traceback.print_exc()

    def metadata_updated(self, session):
        print "metadata_updated called"
        try:
            if not self.queued:
                playlist = self.ctr[self.playlist]
                if playlist.is_loaded():
                    if playlist[self.track].is_loaded():
                        session.load(playlist[self.track])
                        session.play(1)
                        self.queued = True
                        print "Playing", playlist[self.track].name()
        except:
            traceback.print_exc()

    def end_of_track(self, session):
        self.terminate()

    def music_delivery(self, *a, **kw):
        return self.audio.music_delivery(*a, **kw)

if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="spotify username")
    op.add_option("-p", "--password", help="spotify password")
    (options, args) = op.parse_args()
    if not options.username or not options.password:
        op.print_help()
        raise SystemExit
    s = Example1(options.username, options.password)
    s.connect()

