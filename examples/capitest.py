#! /usr/bin/env python

import logging
import os
import time
try:
    import Queue as queue
except ImportError:
    import queue

from spotify import capi

logger = logging.getLogger('capitest')

def main(options):
    cmd_queue = queue.Queue()

    appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')
    appkey = open(appkey_file, mode='rb').read()

    callbacks = capi.sp_session_callbacks(
        logged_in=capi.SP_SESSION_LOGGED_IN_FUNC(
            lambda *a: logger.debug('logged_in called')),
        logged_out=capi.SP_SESSION_LOGGED_OUT_FUNC(
            lambda *a: logger.debug('logged_out called')),
        connection_error=capi.SP_SESSION_CONNECTION_ERROR_FUNC(
            lambda *a: logger.debug('connection_error called')),
        notify_main_thread=capi.SP_SESSION_NOTIFY_MAIN_THREAD_FUNC(
            lambda *a: cmd_queue.put({'command': 'process_events'})),
    )

    config = capi.sp_session_config(
        api_version=capi.SPOTIFY_API_VERSION,
        cache_location='/tmp/libspotify-cache',
        settings_location='/tmp/libspotify-cache',
        application_key=appkey,
        application_key_size=len(appkey),
        user_agent='pyspotify.capi test',
        device_id='pyspotify.capi test',
        tracefile='/tmp/libspotify-cache/trace.log',
    )

    session = capi.sp_session_create(config, callbacks)
    capi.sp_session_login(session, options.username, options.password)

    timeout = 0
    while True:
        try:
            message = cmd_queue.get(timeout=timeout)
            if message.get('command') == 'process_events':
                logger.debug('Got message; processing events')
                timeout = capi.sp_session_process_events(session) / 1000.0
                logger.debug('Will wait %.3fs for next message', timeout)
        except queue.Empty:
            logger.debug(
                'No message received before timeout. Processing events')
            timeout = capi.sp_session_process_events(session) / 1000.0
            logger.debug('Will wait %.3fs for next message', timeout)


if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="Spotify username")
    op.add_option("-p", "--password", help="Spotify password")
    op.add_option("-v", "--verbose", help="Show debug information",
        dest="verbose", action="store_true")
    (options, args) = op.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    main(options)
