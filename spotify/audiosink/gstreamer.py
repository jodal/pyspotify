import threading
import logging
import gobject
import gst
import sys

from spotify.audiosink import BaseAudioSink

logger = logging.getLogger('spotify.audiosink.gstreamer')
gobject.threads_init()

CAPS_TEMPLATE = """
   audio/x-raw-int,
   endianness=(int)%(endianness)s,
   channels=(int)%(channels)d,
   width=(int)16,
   depth=(int)16,
   signed=(boolean)true,
   rate=(int)%(sample_rate)d
"""

class GstreamerSink(BaseAudioSink):
    """
    Audio sink wrapper for systems with Gstreamer installed, which may include
    Linux, Mac OS X, and Windows systems.
    """

    def __init__(self, **kwargs):
        super(GstreamerSink, self).__init__(**kwargs)
        if sys.byteorder == 'little':
            self._endianness = '1234'
        elif sys.byteorder == 'big':
            self._endianness = '4321'
        caps_string = CAPS_TEMPLATE % {
            'endianness': self._endianness,
            'sample_rate': 44100,
            'channels': 2,
        }
        caps = gst.caps_from_string(caps_string)
        self._pipeline = gst.parse_launch(' ! '.join([
            'appsrc name="application_src" block=true',
            'audioconvert',
            'autoaudiosink',
        ]))
        self._source = self._pipeline.get_by_name('application_src')
        self._source.set_property('caps', caps)
        self.mainloop = None
        self.mainloop_thread = threading.Thread(target=self.start_glib)
        self.mainloop_thread.setDaemon(True)
        self.mainloop_thread.start()
        self._setup_message_processor()

    def start_glib(self):
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()
        logger.debug('Mainloop running')

    def _setup_message_processor(self):
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_message)

    def _on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            logger.debug('Track ended')
            self._pipeline.set_state(gst.STATE_NULL)
            self.backend.next()

    def end_of_track(self):
        self._source.emit('end-of-stream')

    def music_delivery(self, session, frames, frame_size, num_frames,
            sample_type, sample_rate, channels):
        assert sample_type == 0, u'Expects 16-bit signed integer samples'
        caps_string = CAPS_TEMPLATE % {
            'endianness': self._endianness,
            'sample_rate': sample_rate,
            'channels': channels,
        }
        caps = gst.caps_from_string(caps_string)
        buffer_ = gst.Buffer(frames)
        buffer_.set_caps(caps)
        self._source.set_property('caps', caps)
        self._source.emit('push-buffer', buffer_)
        return num_frames

    def start(self):
        self._pipeline.set_state(gst.STATE_READY)
        self._pipeline.set_state(gst.STATE_PLAYING)

    def stop(self):
        self._pipeline.set_state(gst.STATE_NULL)

    def pause(self):
        self._pipeline.set_state(gst.STATE_PAUSED)
