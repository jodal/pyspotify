#include <Python.h>
#include <structmember.h>
#include <libgen.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>
#include <stdint.h>
#include "spotify/api.h"
#include "pyspotify.h"
#include "session.h"
#include "track.h"
#include "playlist.h"

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
    fprintf(stderr, "Session_username called\n");
    sp_user *user;
    user = sp_session_user(self->_session);
    if(user == NULL) {
	PyErr_SetString(SpotifyError, "no user returned from session");
	return NULL;
    }
    const char *username = sp_user_canonical_name(user);
    fprintf(stderr, "Session_username completing: %s\n", username);
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
    fprintf(stderr, "Session_logout called\n");
    sp_error error = sp_session_logout(self->_session);
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, "Failed to log out");
        return NULL;
    }
    fprintf(stderr, "Session_logout completing\n");
    return Py_BuildValue("");
};

PyObject *handle_error(err) {
    fprintf(stderr, "Handling error value %d\n", err);
    switch(err) {
	case SP_ERROR_OK:
	    return Py_BuildValue("");
	    break;
	default:
	    PyErr_SetString(SpotifyError, "Error!!!");
	    return NULL;
	    break;
    }
}

static PyObject *Session_playlist_container(Session *self) {
    fprintf(stderr, "entering Session_playlist_container\n");
    sp_playlistcontainer* pc = sp_session_playlistcontainer(self->_session);
    PlaylistContainer *ppc = (PlaylistContainer *)PyObject_CallObject((PyObject *)&PlaylistContainerType, NULL);
    ppc -> _playlistcontainer = pc;
    Py_INCREF(ppc);
    return (PyObject *)ppc;
}

static PyObject *Session_load(Session *self, PyObject *args) {
    fprintf(stderr, "entering Session_load\n");
    Track *track;
    sp_track *t;
    sp_session *s;
    if(!PyArg_ParseTuple(args, "O!", &TrackType, &track)) {
	return NULL;
    }
    t = track->_track;
    s = self->_session;
    fprintf(stderr, "+++++LOADING\n");
    sp_error err = sp_session_player_load(s, t);
    fprintf(stderr, "+++++LOADED\n");
    return handle_error(err);
}

static PyObject *Session_play(Session *self, PyObject *args) {
    int play;
    if(!PyArg_ParseTuple(args, "i", &play))
	return NULL;
    fprintf(stderr, "+++++PLAYING\n");
    return handle_error(sp_session_player_play(self->_session, play));
}

static PyObject *Session_process_events(Session *self) {
    fprintf(stderr, "process events called on %p\n", self);
    int timeout;
    sp_session_process_events(self->_session, &timeout);
    fprintf(stderr, "process events leaving\n");
    return Py_BuildValue("i", timeout);
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
    {NULL}
};

PyTypeObject SessionType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.session.Session",             /*tp_name*/
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
    Session_new,                 /* tp_new */
};

/*************************************/
/*           CALLBACK SHIMS          */
/*************************************/

static void logged_in(sp_session *session, sp_error error) {
    fprintf(stderr, "----------> logged_in called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    fprintf(stderr, "client is %p\n", client);
    PyObject_CallMethod(client, "logged_in", "Oi", psession, error);
    PyGILState_Release(gstate);
}

static void logged_out(sp_session *session) {
    fprintf(stderr, "----------> logged_out called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    fprintf(stderr, "client is %p\n", client);
    PyObject_CallMethod(client, "logged_out", "O", psession);
    PyGILState_Release(gstate);
}

static void metadata_updated(sp_session *session) {
    fprintf(stderr, "----------> metadata_updated called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    fprintf(stderr, "client is %p\n", client);
    PyObject_CallMethod(client, "metadata_updated", "O", psession);
    PyGILState_Release(gstate);
}

static void connection_error(sp_session *session, sp_error error) {
    fprintf(stderr, "----------> connection_error called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    fprintf(stderr, "client is %p\n", client);
    PyObject_CallMethod(client, "connection_error", "Oi", psession, error);
    PyGILState_Release(gstate);
}

static void message_to_user(sp_session *session, const char *message) {
    fprintf(stderr, "----------> message to user: %s", message);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    fprintf(stderr, "client is %p\n", client);
    PyObject_CallMethod(client, "message_to_user", "Os", psession, message);
    PyGILState_Release(gstate);
}

static void notify_main_thread(sp_session *session) {
    //fprintf(stderr, "notify_main_thread called with %p\n", session);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    Py_INCREF(psession);
    //fprintf(stderr, "Session constructed\n");
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    //fprintf(stderr, "client is %p\n", client);
    if(client != NULL) {
	Py_INCREF(client);
	//fprintf(stderr, "waking client\n");
        PyObject_CallMethod(client, "wake", "O", psession);
	//fprintf(stderr, "client awoken\n");
	Py_DECREF(client);
    }
    Py_DECREF(psession);
    //fprintf(stderr, "Releasing GIL\n");
    PyGILState_Release(gstate);
    //fprintf(stderr, "Leaving notify_main_thread\n");
}


static int music_delivery(sp_session *session, const sp_audioformat *format, const void *frames, int num_frames) {
    fprintf(stderr, "----------> music_delivery called\n");
    return num_frames; // consume all of them
}

static void play_token_lost(sp_session *session) {
    fprintf(stderr, "----------> play_token_lost called\n");
}

static void log_message(sp_session *session, const char *data) {
    fprintf(stderr, "----------> log_message called: %s\n", data);
}

static void end_of_track(sp_session *session) {
    fprintf(stderr, "----------> end_of_track called\n");
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

void session_init(PyObject *m) {
    PyModule_AddObject(m, "Session", (PyObject *)&SessionType);
}

PyObject *session_connect(PyObject *self, PyObject *args) {

    PyObject *client;
    if(!PyArg_ParseTuple(args, "O", &client))
	return NULL;
    Py_INCREF(client);

    fprintf(stderr, "client is %p\n", client);
    sp_session_config config;

    config.api_version = SPOTIFY_API_VERSION;
    config.userdata = (void *)client;

    fprintf(stderr, "Setting up configuration...\n");
    PyObject *cache_location = PyObject_GetAttr(client, PyString_FromString("cache_location"));
    if(cache_location == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a cache_location");
        return NULL;
    }
    config.cache_location = PyString_AsString(cache_location);

    fprintf(stderr, "connecting...X\n");
    PyObject *settings_location = PyObject_GetAttr(client, PyString_FromString("settings_location"));
    if(settings_location == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a settings_location");
        return NULL;
    }
    config.settings_location = PyString_AsString(settings_location);

    fprintf(stderr, "connecting...XX\n");
    PyObject *application_key = PyObject_GetAttr(client, PyString_FromString("application_key"));
    if(application_key == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide an application_key");
        return NULL;
    }
    config.application_key = PyString_AsString(application_key);
    config.application_key_size = PyString_Size(application_key);

    fprintf(stderr, "connecting...XXX\n");
    PyObject *user_agent = PyObject_GetAttr(client, PyString_FromString("user_agent"));
    if(user_agent == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a user_agent");
        return NULL;
    }
    config.user_agent = PyString_AsString(user_agent);

    config.callbacks = &g_callbacks;

    sp_session *session;
    sp_error error;
    PyObject *uobj, *pobj;
    char *username, *password;

    fprintf(stderr, "connecting...XXXX\n");
    uobj = PyObject_GetAttr(client, PyString_FromString("username"));
    if(uobj == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a username");
	return NULL;
    }
    username = PyString_AsString(uobj);

    fprintf(stderr, "connecting...YYYYY\n");
    pobj = PyObject_GetAttr(client, PyString_FromString("password"));
    if(pobj == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a password");
	return NULL;
    }
    password = PyString_AsString(pobj);

    fprintf(stderr, "connecting...ZZZZZ\n");
    error = sp_session_init(&config, &session);
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }
    fprintf(stderr, "connecting...M\n");
    error = sp_session_login(session, username, password);
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }
    fprintf(stderr, "connecting...MZ\n");
    Session *psession = (Session *)PyObject_CallObject((PyObject *)&SessionType, NULL);
    fprintf(stderr, "connecting...MZx\n");
    psession->_session = session;
    fprintf(stderr, "connecting...MZy\n");
    Py_INCREF(psession);
    fprintf(stderr, "connecting...MZz\n");
    return (PyObject *)psession;
}
