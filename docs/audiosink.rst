Audio sinks
***********

.. automodule:: spotify.audiosink
    :members:
    :member-order: bysource

Implementations
===============

Implementations of the :class:`BaseAudioSink` interface include:

- :class:`spotify.audiosink.alsa.AlsaSink`

  Requires a system using ALSA, which includes most Linux systems, and the
  `pyalsaaudio <http://pyalsaaudio.sourceforge.net/>`_ library.

- :class:`spotify.audiosink.oss.OssSink`

  Requires a system using OSS or with an OSS emulation, typically a Linux or
  BSD system. Uses the ``ossaudiodev`` module from the Python standard library.

- :class:`spotify.audiosink.portaudio.PortAudioSink`

  Requires a system with the `PortAudio <http://www.portaudio.com/>`_ library
  installed and the Python binding `pyaudio
  <http://people.csail.mit.edu/hubert/pyaudio/>`_. The PortAudio library is
  available for both Linux, Mac OS X, and Windows.

- :class:`spotify.audiosink.gstreamer.GstreamerSink`

  Requires a system with `Gstreamer <http://gstreamer.freedesktop.org/>`_
  installed and the Python bindings gst-python. The Gstreamer library is
  available for both Linux, Mac OS X, and Windows. Though, it isn't always
  trivial to install Gstreamer.
