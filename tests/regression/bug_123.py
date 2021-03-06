from __future__ import print_function

import argparse
import json
import logging
import sys
import threading
import time

import spotify

logger = logging.getLogger(__name__)


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--username",
        action="store",
        required=True,
        help="Spotify username",
    )
    parser.add_argument(
        "-p",
        "--password",
        action="store",
        required=True,
        help="Spotify password",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Turn on debug logging"
    )
    subparsers = parser.add_subparsers(dest="command", help="sub-command --help")

    subparsers.add_parser("info", help="Get account info")

    create_playlist_parser = subparsers.add_parser(
        "create-playlist", help="Create a new playlist"
    )
    create_playlist_parser.add_argument(
        "name", action="store", help="Name of new playlist"
    )

    add_track_parser = subparsers.add_parser("add-track", help="Add track to playlist")
    add_track_parser.add_argument("playlist", action="store", help="URI of playlist")
    add_track_parser.add_argument("track", action="store", help="URI of track")

    return parser


def login(session, username, password):
    logged_in_event = threading.Event()

    def logged_in_listener(session, error_type):
        if error_type != spotify.ErrorType.OK:
            logger.error("Login failed: %r", error_type)
        logged_in_event.set()

    session.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)
    session.login(username, password)

    if not logged_in_event.wait(10):
        raise RuntimeError("Login timed out")
    logger.debug("Logged in as %r", session.user_name)

    while session.connection.state != spotify.ConnectionState.LOGGED_IN:
        logger.debug("Waiting for connection")
        time.sleep(0.1)


def logout(session):
    logged_out_event = threading.Event()

    def logged_out_listener(session):
        logged_out_event.set()

    session.on(spotify.SessionEvent.LOGGED_OUT, logged_out_listener)
    session.logout()

    if not logged_out_event.wait(10):
        raise RuntimeError("Logout timed out")


def create_playlist(session, playlist_name):
    playlist = session.playlist_container.add_new_playlist(playlist_name)

    return (playlist.name, playlist.link.uri)


def add_track(session, playlist_uri, track_uri):
    playlist = session.get_playlist(playlist_uri).load()
    track = session.get_track(track_uri).load()

    playlist.add_tracks(track)

    return playlist.link.uri, track.link.uri


def main(args):
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    session = spotify.Session()
    loop = spotify.EventLoop(session)
    loop.start()

    login(session, args.username, args.password)

    try:
        if args.command == "info":
            session.playlist_container.load()
            result = {
                "success": True,
                "action": args.command,
                "response": {
                    "user_name": session.user_name,
                    "num_playlists": len(session.playlist_container),
                    "num_starred": len(session.starred.tracks),
                },
            }
        elif args.command == "create-playlist":
            name, uri = create_playlist(session, args.name)
            result = {
                "success": True,
                "action": args.command,
                "response": {"playlist_name": name, "playlist_uri": uri},
            }
        elif args.command == "add-track":
            playlist_uri, track_uri = add_track(session, args.playlist, args.track)
            result = {
                "success": True,
                "action": args.command,
                "response": {
                    "playlist_uri": playlist_uri,
                    "track_uri": track_uri,
                },
            }
    except spotify.Error as error:
        logger.exception("%s failed", args.command)
        result = {"success": False, "action": args.command, "error": str(error)}

    # Proper logout ensures that all data is persisted properly
    logout(session)

    return result


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    result = main(args)
    print(json.dumps(result, indent=2))
    sys.exit(not result["success"])
