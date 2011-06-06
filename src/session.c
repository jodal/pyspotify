/* $Id$
 *
 * Copyright 2009 Doug Winter
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0PyDe
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

#include <Python.h>
#include <structmember.h>
#include <libgen.h>
#include <unistd.h>
#include <stdint.h>
#include <pthread.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "album.h"
#include "albumbrowser.h"
#include "artist.h"
#include "artistbrowser.h"
#include "session.h"
#include "track.h"
#include "playlist.h"
#include "playlistcontainer.h"
#include "search.h"
#include "image.h"

static int session_constructed = 0;

static PyObject *PyTuple_NewByPreappending(PyObject *firstObject, PyObject *tuple)
{
    PyObject *result = PyTuple_New(PyObject_Length(tuple) + 1);
    PyTuple_SetItem(result, 0, firstObject);
    Py_XINCREF(firstObject);

    unsigned i;
    for (i = 0; i < PyObject_Length(tuple); ++i) {
        PyObject *member = PyTuple_GetItem(tuple, i);
        Py_XINCREF(member);
        PyTuple_SetItem(result, i + 1, member);
    }

    return result;
}

static PyObject *Session_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Session *self;

    self = (Session *)type->tp_alloc(type, 0);
    self->_session = NULL;
    return (PyObject *)self;
}

static PyMemberDef Session_members[] = {
    {NULL}
};

static PyObject *Session_username(Session *self) {
    sp_user *user;
    user = sp_session_user(self->_session);
    if(user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    const char *username = sp_user_canonical_name(user);
    return PyString_FromString(username);
};

static PyObject *Session_display_name(Session *self) {
    sp_user *user;

    user = sp_session_user(self->_session);
    if(user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    const char *username = sp_user_display_name(user);
    return PyString_FromString(username);
};

static PyObject *Session_user_is_loaded(Session *self) {
    sp_user *user;

    user = sp_session_user(self->_session);
    if(user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    bool loaded = sp_user_is_loaded(user);
    return Py_BuildValue("i", loaded);
};

static PyObject *Session_logout(Session *self) {
    Py_BEGIN_ALLOW_THREADS
    sp_session_logout(self->_session);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
};

PyObject *handle_error(int err) {
    if(err != 0) {
	PyErr_SetString(SpotifyError, sp_error_message(err));
	return NULL;
    } else {
	Py_RETURN_NONE;
    }
}

const char *error_message(int err) {
    if(err != 0) {
        return sp_error_message(err);
    } else {
        return NULL;
    }
}

static PyObject *Session_playlist_container(Session *self) {
    sp_playlistcontainer* pc;
    Py_BEGIN_ALLOW_THREADS
    pc = sp_session_playlistcontainer(self->_session);
    Py_END_ALLOW_THREADS
    PlaylistContainer *ppc = (PlaylistContainer *)PyObject_CallObject((PyObject *)&PlaylistContainerType, NULL);
    ppc -> _playlistcontainer = pc;
    sp_playlistcontainer_add_ref(pc);
    return (PyObject *)ppc;
}

static PyObject *Session_load(Session *self, PyObject *args) {
    Track *track;
    sp_track *t;
    sp_session *s;
    sp_error err;
    if(!PyArg_ParseTuple(args, "O!", &TrackType, &track)) {
	return NULL;
    }
    t = track->_track;
    s = self->_session;
    Py_BEGIN_ALLOW_THREADS
    err = sp_session_player_load(s, t);
    Py_END_ALLOW_THREADS
    return handle_error(err);
}

static PyObject *Session_seek(Session *self, PyObject *args) {
    int seek;
    if(!PyArg_ParseTuple(args, "i", &seek))
	return NULL;
    Py_BEGIN_ALLOW_THREADS
    sp_session_player_seek(self->_session, seek);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *Track_is_available(Session *self, PyObject *args) {
    Track *track;
    if(!PyArg_ParseTuple(args, "O!", &TrackType, &track)) {
    return NULL;
    }
    return Py_BuildValue("i", sp_track_is_available(self->_session, track->_track));
}

static PyObject *Track_is_local(Session *self, PyObject *args) {
    Track *track;
    if(!PyArg_ParseTuple(args, "O!", &TrackType, &track)) {
    return NULL;
    }
    return Py_BuildValue("i", sp_track_is_local(self->_session, track->_track));
}

static PyObject *Session_play(Session *self, PyObject *args) {
    int play;
    if(!PyArg_ParseTuple(args, "i", &play))
	return NULL;
    Py_BEGIN_ALLOW_THREADS
    sp_session_player_play(self->_session, play);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *Session_unload(Session *self) {
    sp_session_player_unload(self->_session);
    Py_RETURN_NONE;
}

static PyObject *Session_process_events(Session *self) {
    int timeout;
    Py_BEGIN_ALLOW_THREADS
    sp_session_process_events(self->_session, &timeout);
    Py_END_ALLOW_THREADS
    return Py_BuildValue("i", timeout);
}

void search_complete(sp_search *search, Callback *st) {
    PyObject *results;
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    results = Results_FromSpotify(search);
    PyObject_CallFunctionObjArgs(st->callback, results, st->userdata, NULL);
    delete_trampoline(st);
    Py_DECREF(results);
    PyGILState_Release(gstate);
}

static PyObject *Session_search(Session *self, PyObject *args, PyObject *kwds) {
    char *query;
    sp_search *search;
    PyObject *callback, *userdata = NULL;
    int track_offset=0, track_count=32,
        album_offset=0, album_count=32,
	artist_offset=0, artist_count=32;
    Callback *st;
    PyObject *results;

    static char *kwlist[] = {"query", "callback",
                             "track_offset", "track_count",
			     "album_offset", "album_count",
			     "artist_offset", "artist_count",
			     "userdata", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "sO|iiiiiiO", kwlist, &query, &callback,
				&track_offset, &track_count, &album_offset, &album_count,
				&artist_offset, &artist_count, &userdata);
    if (userdata != NULL)
        Py_INCREF(userdata);
    Py_INCREF(callback);
    st = malloc(sizeof(Callback));
    st->userdata = userdata;
    st->manager = NULL;
    st->callback = callback;
    Py_BEGIN_ALLOW_THREADS
    search = sp_search_create(self->_session, query,
			      track_offset, track_count,
			      album_offset, album_count,
			      artist_offset, artist_count,
			      (search_complete_cb *)search_complete, (void *)st);
    Py_END_ALLOW_THREADS
    results = Results_FromSpotify(search);
    return results;
}

static PyObject *Session_browse_album(Session *self, PyObject *args, PyObject *kwds)
{
    PyObject *album, *callback, *userdata = NULL;
    static char *kwlist[] = {"artist", "callback", "userdata", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O|O", kwlist, &AlbumType, &album, &callback, &userdata))
        return NULL;

    args = PyTuple_NewByPreappending((PyObject *)self, args);
    PyObject *result = PyObject_Call((PyObject *)&AlbumBrowserType, args, kwds);
    Py_XDECREF(args);
    return result;
}

static PyObject *Session_browse_artist(Session *self, PyObject *args, PyObject *kwds)
{
    PyObject *artist, *callback, *userdata = NULL;
    static char *kwlist[] = {"artist", "callback", "userdata", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O|O", kwlist, &ArtistType, &artist, &callback, &userdata))
        return NULL;

    args = PyTuple_NewByPreappending((PyObject *)self, args);
    PyObject *result = PyObject_Call((PyObject *)&ArtistBrowserType, args, kwds);
    Py_XDECREF(args);
    return result;
}

static PyObject *Session_image_create(Session *self, PyObject *args) {
    byte *image_id;
    size_t len;
    sp_image *image;
    PyObject *i;

    if(!PyArg_ParseTuple(args, "s#", &image_id, &len))
	return NULL;
    assert(len == 20);
    image = sp_image_create(self->_session, image_id);
    i = Image_FromSpotify(image);
    return i;
}

static PyObject *Session_set_preferred_bitrate(Session *self, PyObject *args) {
    int bitrate;
    if(!PyArg_ParseTuple(args, "i", &bitrate))
	return NULL;
    Py_BEGIN_ALLOW_THREADS
    sp_session_preferred_bitrate(self->_session, bitrate);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *Session_starred(Session *self) {
    sp_playlist *spl;
    Py_BEGIN_ALLOW_THREADS
    spl = sp_session_starred_create(self->_session);
    Py_END_ALLOW_THREADS
    PyObject *pl = Playlist_FromSpotify(spl);
    return pl;
}

static PyMethodDef Session_methods[] = {
    {"username", (PyCFunction)Session_username, METH_NOARGS, "Return the canonical username for the logged in user"},
    {"display_name", (PyCFunction)Session_display_name, METH_NOARGS, "Return the full name for the logged in user"},
    {"user_is_loaded", (PyCFunction)Session_user_is_loaded, METH_NOARGS, "Return whether the user is loaded or not"},
    {"logout", (PyCFunction)Session_logout, METH_NOARGS, "Logout from the session and terminate the main loop"},
    {"process_events", (PyCFunction)Session_process_events, METH_NOARGS, "Process any outstanding events"},
    {"load", (PyCFunction)Session_load, METH_VARARGS, "Load the specified track on the player"},
    {"seek", (PyCFunction)Session_seek, METH_VARARGS, "Seek the currently loaded track"},
    {"play", (PyCFunction)Session_play, METH_VARARGS, "Play or pause the currently loaded track"},
    {"unload", (PyCFunction)Session_unload, METH_NOARGS, "Stop the currently playing track"},
    {"is_available", (PyCFunction)Track_is_available, METH_VARARGS, "Return true if the track is available for playback."},
    {"is_local", (PyCFunction)Track_is_local, METH_VARARGS, "Return true if the track is a local file."},
    {"playlist_container", (PyCFunction)Session_playlist_container, METH_NOARGS, "Return the playlist container for the currently logged in user"},
    {"browse_album", (PyCFunction)Session_browse_album, METH_VARARGS | METH_KEYWORDS, "Browse an album, calling the callback when the browse request completes"},
    {"browse_artist", (PyCFunction)Session_browse_artist, METH_VARARGS | METH_KEYWORDS, "Browse an artist, calling the callback when the browse request completes"},
    {"search", (PyCFunction)Session_search, METH_VARARGS | METH_KEYWORDS, "Conduct a search, calling the callback when results are available"},
    {"image_create", (PyCFunction)Session_image_create, METH_VARARGS, "Create an image of album cover art"},
    {"set_preferred_bitrate", (PyCFunction)Session_set_preferred_bitrate, METH_VARARGS, "Set the preferred bitrate of the audio stream. 0 = 160k, 1 = 320k"},
    {"starred", (PyCFunction)Session_starred, METH_NOARGS, "Get the starred playlist for the logged in user"},
    {NULL}
};

PyTypeObject SessionType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_spotify.Session",             /*tp_name*/
    sizeof(Session),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,			       /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Session objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Session_methods,             /* tp_methods */
    Session_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,      /* tp_init */
    0,                         /* tp_alloc */
    Session_new                /* tp_new */
};

/*************************************/
/*           CALLBACK SHIMS          */
/*************************************/

static void logged_in(sp_session *session, sp_error error) {
    // fprintf(stderr, "----------> logged_in called\n");
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "logged_in", "Os", psession, error_message(error));
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void logged_out(sp_session *session) {
    // fprintf(stderr, "----------> logged_out called\n");
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "logged_out", "O", psession);
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void metadata_updated(sp_session *session) {
    // fprintf(stderr, "----------> metadata_updated called\n");
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "metadata_updated", "O", psession);
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void connection_error(sp_session *session, sp_error error) {
    // fprintf(stderr, "----------> connection_error called\n");
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "connection_error", "Os", psession, error_message(error));
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void message_to_user(sp_session *session, const char *message) {
    // fprintf(stderr, "----------> message to user: %s\n", message);
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "message_to_user", "Os", psession, message);
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void notify_main_thread(sp_session *session) {
    // fprintf(stderr, "----------> notify_main_thread\n");
    PyGILState_STATE gstate;
    PyObject *res = NULL;

    if(!session_constructed)
        return;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    if(client != NULL) {
        res = PyObject_CallMethod(client, "wake", "O", psession);
    }
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static int frame_size(const sp_audioformat *format) {
    switch(format->sample_type) {
	case SP_SAMPLETYPE_INT16_NATIVE_ENDIAN:
	    return format->channels * 2; // 16 bits = 2 bytes
	    break;
	default:
	    return -1;
    }
}

static int music_delivery(sp_session *session, const sp_audioformat *format, const void *frames, int num_frames) {
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    int siz = frame_size(format);
    PyObject *pyframes = PyBuffer_FromMemory((void *)frames, num_frames * siz);
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject *c= PyObject_CallMethod(client, "music_delivery", "OOiiiii", psession, pyframes, siz, num_frames, format->sample_type, format->sample_rate, format->channels);
    int consumed = num_frames; // assume all consumed
    if(c != NULL && PyObject_TypeCheck(c, &PyInt_Type)) {
	consumed = (int)PyInt_AsLong(c);
    }
    Py_DECREF(pyframes);
    Py_DECREF(psession);
    Py_XDECREF(c);
    PyGILState_Release(gstate);
    return consumed;
}

static void play_token_lost(sp_session *session) {
    // fprintf(stderr, "----------> play_token_lost called\n");
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "play_token_lost", "O", psession);
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void log_message(sp_session *session, const char *data) {
    // fprintf(stderr, "----------> log_message called: %s\n", data);
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "log_message", "Os", psession, data);
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static void end_of_track(sp_session *session) {
    // fprintf(stderr, "----------> end_of_track called\n");
    PyGILState_STATE gstate;
    PyObject *res;

    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    res = PyObject_CallMethod(client, "end_of_track", "O", psession);
    Py_DECREF(psession);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

void session_init(PyObject *m) {
    Py_INCREF(&SessionType);
    PyModule_AddObject(m, "Session", (PyObject *)&SessionType);
}

char *copystring(PyObject *ob) {
    char *s = PyString_AsString(ob);
    char *s2 = PyMem_Malloc(strlen(s) +1);
    strcpy(s2, s);
    return s2;
}

static sp_session_callbacks g_callbacks = {
    &logged_in,
    &logged_out,
    &metadata_updated,
    &connection_error,
    &message_to_user,
    &notify_main_thread,
    &music_delivery,
    &play_token_lost,
    &log_message,
    &end_of_track
};

PyObject *session_connect(PyObject *self, PyObject *args) {
#ifdef DEBUG
    fprintf(stderr, "> entering session_connect\n");
#endif
    sp_session_config config;
    memset(&config, 0, sizeof(config));

    PyObject *client;
    sp_session *session;
    sp_error error;
    PyObject *uobj, *pobj;
    char *username, *password;

    if(!PyArg_ParseTuple(args, "O", &client))
	return NULL;

    PyEval_InitThreads();
    config.api_version = SPOTIFY_API_VERSION;
    config.userdata = (void *)client;
    config.callbacks = &g_callbacks;
    config.user_agent = "unset";


#ifdef DEBUG
    fprintf(stderr, "Config mark 1\n");
#endif
    PyObject *cache_location = PyObject_GetAttr(client, PyString_FromString("cache_location"));
#ifdef DEBUG
    fprintf(stderr, "Cache location is '%s'\n", PyString_AsString(cache_location));
#endif
    if(cache_location == NULL) {

        return NULL;
    }
#ifdef DEBUG
    fprintf(stderr, "Config mark 1.1\n");
#endif
    config.cache_location = copystring(cache_location);

#ifdef DEBUG
    fprintf(stderr, "Config mark 2\n");
#endif
    PyObject *settings_location = PyObject_GetAttr(client, PyString_FromString("settings_location"));
    if(settings_location == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a settings_location");
        return NULL;
    }
    config.settings_location = copystring(settings_location);

#ifdef DEBUG
    fprintf(stderr, "Config mark 3\n");
#endif
    PyObject *application_key = PyObject_GetAttr(client, PyString_FromString("application_key"));
    if(application_key == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide an application_key");
        return NULL;
    }
    char *s_appkey;
    Py_ssize_t l_appkey;
    PyString_AsStringAndSize(application_key, &s_appkey, &l_appkey);
    config.application_key_size = l_appkey;
    config.application_key = PyMem_Malloc(l_appkey);
    memcpy((char *)config.application_key, s_appkey, l_appkey);

#ifdef DEBUG
    fprintf(stderr, "Config mark 4\n");
#endif
    PyObject *user_agent = PyObject_GetAttr(client, PyString_FromString("user_agent"));
    if(user_agent == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a user_agent");
        return NULL;
    }
    config.user_agent = copystring(user_agent);

#ifdef DEBUG
    fprintf(stderr, "Config mark 5\n");
#endif
    uobj = PyObject_GetAttr(client, PyString_FromString("username"));
    if(uobj == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a username");
	return NULL;
    }
    username = copystring(uobj);

    pobj = PyObject_GetAttr(client, PyString_FromString("password"));
    if(pobj == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a password");
	return NULL;
    }
    password = copystring(pobj);

    Py_BEGIN_ALLOW_THREADS
#ifdef DEBUG
    fprintf(stderr, "Calling sp_session_init\n");
#endif
    error = sp_session_create(&config, &session);
#ifdef DEBUG
    fprintf(stderr, "Returned from sp_session_init\n");
#endif
    Py_END_ALLOW_THREADS
    session_constructed = 1;
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    sp_session_login(session, username, password);
    Py_END_ALLOW_THREADS
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    return (PyObject *)psession;
}
