/* $Id$
 *
 * Copyright 2009 Doug Winter
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
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
#include "spotify/api.h"
#include "pyspotify.h"
#include "session.h"
#include "track.h"
#include "playlist.h"
#include "search.h"
#include "image.h"

// define DEBUG to get lots of extra crap printed out
//#define DEBUG 1

static int session_constructed = 0;

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
	PyErr_SetString(SpotifyError, "no user returned from session");
	return NULL;
    }
    const char *username = sp_user_canonical_name(user);
    return PyString_FromString(username);
};

static PyObject *Session_display_name(Session *self) {
    sp_user *user;

    user = sp_session_user(self->_session);
    if(user == NULL)
	return NULL;
    const char *username = sp_user_display_name(user);
    return PyString_FromString(username);
};

static PyObject *Session_user_is_loaded(Session *self) {
    sp_user *user;

    user = sp_session_user(self->_session);
    if(user == NULL)
	return NULL;
    bool loaded = sp_user_is_loaded(user);
    return Py_BuildValue("i", loaded);
};

static PyObject *Session_logout(Session *self) {
    sp_error error;
    Py_BEGIN_ALLOW_THREADS
    error = sp_session_logout(self->_session);
    Py_END_ALLOW_THREADS
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, "Failed to log out");
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
};

PyObject *handle_error(int err) {
    if(err != 0) {
	PyErr_SetString(SpotifyError, sp_error_message(err));
	return NULL;
    } else {
	Py_INCREF(Py_None);
	return Py_None;
    }
}

static PyObject *Session_playlist_container(Session *self) {
    sp_playlistcontainer* pc;
    Py_BEGIN_ALLOW_THREADS
    pc = sp_session_playlistcontainer(self->_session);
    Py_END_ALLOW_THREADS
    PlaylistContainer *ppc = (PlaylistContainer *)PyObject_CallObject((PyObject *)&PlaylistContainerType, NULL);
    Py_INCREF(ppc);
    ppc -> _playlistcontainer = pc;
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
    Py_INCREF(track);
    t = track->_track;
    s = self->_session;
    Py_BEGIN_ALLOW_THREADS
    err = sp_session_player_load(s, t);
    Py_END_ALLOW_THREADS
    return handle_error(err);
}

static PyObject *Session_play(Session *self, PyObject *args) {
    int play;
    sp_error err;
    if(!PyArg_ParseTuple(args, "i", &play))
	return NULL;
    Py_BEGIN_ALLOW_THREADS
    err = sp_session_player_play(self->_session, play);
    Py_END_ALLOW_THREADS
    return handle_error(err);
}

static PyObject *Session_process_events(Session *self) {
    int timeout;
    Py_BEGIN_ALLOW_THREADS
    sp_session_process_events(self->_session, &timeout);
    Py_END_ALLOW_THREADS
    return Py_BuildValue("i", timeout);
}

typedef struct {
    PyObject *callback;
    PyObject *userdata;
} search_trampoline;

void search_complete(sp_search *search, search_trampoline *st) {
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Results *results = (Results *)PyObject_CallObject((PyObject *)&ResultsType, NULL);
    Py_INCREF(results);
    results->_search = search;
    PyObject_CallFunctionObjArgs(st->callback, results, st->userdata, NULL);
    Py_DECREF(results);
    PyGILState_Release(gstate);
}

static PyObject *Session_search(Session *self, PyObject *args, PyObject *kwds) {
    char *query;
    sp_search *search;
    PyObject *callback, *userdata;
    int track_offset=0, track_count=32,
        album_offset=0, album_count=32,
	artist_offset=0, artist_count=32;
    search_trampoline *st;
    static char *kwlist[] = {"query", "callback",
                             "track_offset", "track_count",
			     "album_offset", "album_count",
			     "artist_offset", "artist_count",
			     "userdata", NULL};
    PyArg_ParseTupleAndKeywords(args, kwds, "sO|iiiiiiO", kwlist, &query, &callback,
				&track_offset, &track_count, &album_offset, &album_count,
				&artist_offset, &artist_count, &userdata);
    Py_INCREF(userdata);
    Py_INCREF(callback);
    st = malloc(sizeof(search_trampoline));
    st->userdata = userdata;
    st->callback = callback;
    Py_BEGIN_ALLOW_THREADS
    search = sp_search_create(self->_session, query,
			      track_offset, track_count,
			      album_offset, album_count,
			      artist_offset, artist_count,
			      search_complete, (void *)st);
    Py_END_ALLOW_THREADS
    Results *results = (Results *)PyObject_CallObject((PyObject *)&ResultsType, NULL);
    Py_INCREF(results);
    results->_search = search;
    return (PyObject *)results;
}

PyObject *Session_image_create(Session *self, PyObject *args) {
    char *image_id;
    size_t len;
    if(!PyArg_ParseTuple(args, "s#", &image_id, &len))
	return NULL;
    assert(len == 20);
    Image *i = PyObject_CallObject((PyObject *)&ImageType, NULL);
    i->_image = sp_image_create(self->_session, image_id);
    return (PyObject *)i;
}

static PyMethodDef Session_methods[] = {
    {"username", (PyCFunction)Session_username, METH_NOARGS, "Return the canonical username for the logged in user"},
    {"display_name", (PyCFunction)Session_display_name, METH_NOARGS, "Return the full name for the logged in user"},
    {"user_is_loaded", (PyCFunction)Session_user_is_loaded, METH_NOARGS, "Return whether the user is loaded or not"},
    {"logout", (PyCFunction)Session_logout, METH_NOARGS, "Logout from the session and terminate the main loop"},
    {"process_events", (PyCFunction)Session_process_events, METH_NOARGS, "Process any outstanding events"},
    {"load", (PyCFunction)Session_load, METH_VARARGS, "Load the specified track on the player"},
    {"play", (PyCFunction)Session_play, METH_VARARGS, "Play or pause the currently loaded track"},
    {"playlist_container", (PyCFunction)Session_playlist_container, METH_NOARGS, "Return the playlist container for the currently logged in user"},
    {"search", (PyCFunctionWithKeywords)Session_search, METH_KEYWORDS, "Conduct a search, calling the callback when results are available"},
    {"image_create", (PyCFunction)Session_image_create, METH_VARARGS, "Create an image of album cover art"},
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
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "logged_in", "Oi", psession, error);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void logged_out(sp_session *session) {
    // fprintf(stderr, "----------> logged_out called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "logged_out", "O", psession);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void metadata_updated(sp_session *session) {
    // fprintf(stderr, "----------> metadata_updated called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "metadata_updated", "O", psession);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void connection_error(sp_session *session, sp_error error) {
    // fprintf(stderr, "----------> connection_error called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "connection_error", "Oi", psession, error);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void message_to_user(sp_session *session, const char *message) {
    // fprintf(stderr, "----------> message to user: %s\n", message);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "message_to_user", "Os", psession, message);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void notify_main_thread(sp_session *session) {
    // fprintf(stderr, "----------> notify_main_thread\n");
    if(!session_constructed) return;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    if(client != NULL) {
        PyObject_CallMethod(client, "wake", "O", psession);
    }
    Py_DECREF(psession);
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
    Py_INCREF(pyframes);
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject *c= PyObject_CallMethod(client, "music_delivery", "OOiiiii", psession, pyframes, siz, num_frames, format->sample_type, format->sample_rate, format->channels);
    int consumed = num_frames; // assume all consumed
    if(PyObject_TypeCheck(c, &PyInt_Type)) {
	consumed = (int)PyInt_AsLong(c);
    }
    Py_DECREF(pyframes);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
    return consumed;
}

static void play_token_lost(sp_session *session) {
    // fprintf(stderr, "----------> play_token_lost called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "play_token_lost", "O", psession);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void log_message(sp_session *session, const char *data) {
    // fprintf(stderr, "----------> log_message called: %s\n", data);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "log_message", "Os", psession, data);
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static void end_of_track(sp_session *session) {
    // fprintf(stderr, "----------> end_of_track called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    PyObject_CallMethod(client, "end_of_track", "O", psession);
    Py_DECREF(psession);
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
	PyErr_SetString(SpotifyError, "Client did not provide a cache_location");
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
    memcpy(config.application_key, s_appkey, l_appkey);

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
    error = sp_session_init(&config, &session);
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
    error = sp_session_login(session, username, password);
    Py_END_ALLOW_THREADS
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    psession->_session = session;
    return (PyObject *)psession;
}
