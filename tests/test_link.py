from __future__ import unicode_literals

import gc
import mock
import unittest

import spotify


@mock.patch('spotify.link.lib')
class LinkTest(unittest.TestCase):

    def setUp(self):
        spotify.session_instance = mock.sentinel.session

    def tearDown(self):
        spotify.session_instance = None

    def test_create_from_string(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link

        spotify.Link('spotify:track:foo')

        lib_mock.sp_link_create_from_string.assert_called_once_with(
            mock.ANY)
        self.assertEqual(
            spotify.ffi.string(
                lib_mock.sp_link_create_from_string.call_args[0][0]),
            b'spotify:track:foo')

    @mock.patch('spotify.track.lib')
    def test_create_from_track(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_track.return_value = sp_link
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        link = spotify.Link(track)

        self.assertEqual(link.sp_link, sp_link)
        lib_mock.sp_link_create_from_track.assert_called_once_with(
            sp_track, 0)

    @mock.patch('spotify.track.lib')
    def test_create_from_track_and_offset(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_track.return_value = sp_link
        sp_track = spotify.ffi.new('int *')
        track = spotify.Track(sp_track)

        link = spotify.Link(track, offset=90)

        self.assertEqual(link.sp_link, sp_link)
        lib_mock.sp_link_create_from_track.assert_called_once_with(
            sp_track, 90)

    @mock.patch('spotify.playlist.lib')
    def test_create_from_playlist(self, playlist_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_playlist.return_value = sp_link
        sp_playlist = spotify.ffi.new('int *')
        playlist = spotify.Playlist(sp_playlist)

        link = spotify.Link(playlist)

        self.assertEqual(link.sp_link, sp_link)
        lib_mock.sp_link_create_from_playlist.assert_called_once_with(
            sp_playlist)

    @mock.patch('spotify.user.lib')
    def test_create_from_user(self, user_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_user.return_value = sp_link
        sp_user = spotify.ffi.new('int *')
        user = spotify.User(sp_user)

        link = spotify.Link(user)

        self.assertEqual(link.sp_link, sp_link)
        lib_mock.sp_link_create_from_user.assert_called_once_with(sp_user)

    def test_raises_error_if_session_doesnt_exist(self, lib_mock):
        spotify.session_instance = None

        self.assertRaises(RuntimeError, spotify.Link, 'spotify:track:foo')

    def test_raises_error_if_string_isnt_parseable(self, lib_mock):
        lib_mock.sp_link_create_from_string.return_value = spotify.ffi.NULL

        self.assertRaises(ValueError, spotify.Link, 'invalid link string')

    def test_releases_sp_link_when_link_dies(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link

        link = spotify.Link('spotify:track:foo')
        link = None  # noqa
        gc.collect()  # Needed for PyPy

        lib_mock.sp_link_release.assert_called_with(sp_link)

    def test_str_grows_buffer_to_fit_link(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        string = 'foo' * 100

        def func(sp_link, buffer_, buffer_size):
            # -1 to keep a char free for \0 terminating the string
            length = min(len(string), buffer_size - 1)
            # Due to Python 3 treating bytes as an array of ints, we have to
            # encode and copy chars one by one.
            for i in range(length):
                buffer_[i] = string[i].encode('utf-8')
            return len(string)

        lib_mock.sp_link_as_string.side_effect = func
        link = spotify.Link(string)

        result = str(link)

        lib_mock.sp_link_as_string.assert_called_with(
            sp_link, mock.ANY, mock.ANY)
        self.assertEqual(result, string)

    def test_has_type_constants(self, lib_mock):
        self.assertEqual(spotify.Link.TYPE_TRACK, 1)
        self.assertEqual(spotify.Link.TYPE_ALBUM, 2)

    def test_type(self, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_type.return_value = 1

        link = spotify.Link('spotify:track:foo')
        self.assertEqual(spotify.Link.TYPE_TRACK, link.type)

        lib_mock.sp_link_type.assert_called_once_with(sp_link)

    @mock.patch('spotify.track.lib')
    def test_as_track(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_track = spotify.ffi.new('int *')
        lib_mock.sp_link_as_track.return_value = sp_track

        link = spotify.Link('spotify:track:foo')
        self.assertEqual(link.as_track().sp_track, sp_track)

        lib_mock.sp_link_as_track.assert_called_once_with(sp_link)

    @mock.patch('spotify.track.lib')
    def test_as_track_if_not_a_track(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_track.return_value = spotify.ffi.NULL

        link = spotify.Link('spotify:track:foo')
        self.assertIsNone(link.as_track())

        lib_mock.sp_link_as_track.assert_called_once_with(sp_link)

    @mock.patch('spotify.track.lib')
    def test_as_track_with_offset(self, track_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_track = spotify.ffi.new('int *')
        lib_mock.sp_link_as_track_and_offset.return_value = sp_track

        link = spotify.Link('spotify:track:foo')
        track = link.as_track(offset=90)

        self.assertEqual(track.sp_track, sp_track)

        lib_mock.sp_link_as_track_and_offset.assert_called_once_with(
            sp_link, 90)

    @mock.patch('spotify.user.lib')
    def test_as_user(self, user_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        sp_user = spotify.ffi.new('int *')
        lib_mock.sp_link_as_user.return_value = sp_user

        link = spotify.Link('spotify:user:foo')
        self.assertEqual(link.as_user().sp_user, sp_user)

        lib_mock.sp_link_as_user.assert_called_once_with(sp_link)

    @mock.patch('spotify.user.lib')
    def test_as_user_if_not_a_user(self, user_lib_mock, lib_mock):
        sp_link = spotify.ffi.new('int *')
        lib_mock.sp_link_create_from_string.return_value = sp_link
        lib_mock.sp_link_as_user.return_value = spotify.ffi.NULL

        link = spotify.Link('spotify:user:foo')
        self.assertIsNone(link.as_user())

        lib_mock.sp_link_as_user.assert_called_once_with(sp_link)
