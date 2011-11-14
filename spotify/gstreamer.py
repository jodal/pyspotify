import gst
import gobject
gobject.threads_init()

DEFAULT_CAPSET = gst.Caps('''\
audio/x-raw-int,
endianness=(int)1234,
channels=(int)2,
width=(int)16,
depth=(int)16,
signed=(boolean)true,
rate=(int)44100''')

class GstreamerAudioController(object):
    '''
    Wrapper around gstreamer so that we can use Gstreamer for audio handling,
    and thus allowing the pyspotify client to work on OS X.
    '''

    def __init__(self):
        self.pipeline = gst.parse_launch(' ! '.join(
                ['appsrc name="application_src" block=1',
                 'audioconvert',
                 'autoaudiosink']
                )
                                         )
        self.source = self.pipeline.get_by_name('application_src')
        self.source.set_property('caps', DEFAULT_CAPSET)
        self.paused = True
        self.backend = None

    def set_backend(self, backend):
        self.backend = backend

    def music_delivery(self,
                       session,
                       frames,
                       frame_size,
                       num_frames,
                       sample_type,
                       sample_rate,
                       channels):
        assert sample_type == 0, u'Expects 16-bit signed integer samples'
        capabilites = """
            audio/x-raw-int,
            endianness=(int)1234,
            channels=(int)%(channels)d,
            width=(int)16,
            depth=(int)16,
            signed=(boolean)true,
            rate=(int)%(sample_rate)d
        """ % {
            'sample_rate': sample_rate,
            'channels': channels,
        }
        self.emit_data(capabilites, bytes(frames))
        return num_frames

    def _on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            print 'EOS'
            self.stop()
        elif message.type == gst.MESSAGE_ERROR:
            error, debug = message.parse_error()
            print error, debug
            self.stop()
        elif message.type == gst.MESSAGE_WARNING:
            error, debug = message.parse_warning()
            print error, debug

    def emit_data(self, capabilities, data):
        """
        Call this to deliver raw audio data to be played.

        :param capabilities: a GStreamer capabilities string
        :type capabilities: string
        :param data: raw audio data to be played
        """
        if self.paused:
            return
        caps = gst.caps_from_string(capabilities)
        buffer_ = gst.Buffer(buffer(data))
        buffer_.set_caps(caps)
        self.source.set_property('caps', caps)
        self.source.emit('push-buffer', buffer_)

    def start(self):
        """
        Notify GStreamer that it should start playback.

        :rtype: :class:`True` if successfull, else :class:`False`
        """
        self.paused = False
        self.prepare_change()
        return self.pipeline.set_state(gst.STATE_PLAYING)

    def stop(self):
        """
        Notify GStreamer that it should stop playback.

        :rtype: :class:`True` if successfull, else :class:`False`
        """
        self.paused = True
        self.prepare_change()
        return self.pipeline.set_state(gst.STATE_NULL)

    def pause(self):
        """
        Notify GStreamer that it should pause playback.

        :rtype: :class:`True` if successfull, else :class:`False`
        """
        self.paused = True
        self.prepare_change()
        return self.pipeline.set_state(gst.STATE_PAUSED)

    def prepare_change(self):
        """
        Notify GStreamer that we are about to change state of playback.

        This function *MUST* be called before changing URIs or doing
        changes like updating data that is being pushed. The reason for this
        is that GStreamer will reset all its state when it changes to
        :attr:`gst.STATE_READY`.
        """
        return self.pipeline.set_state(gst.STATE_READY)
