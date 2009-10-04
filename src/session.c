#include <Python.h>
#include <structmember.h>
#include <libgen.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>
#include <stdint.h>
#include "spotify/api.h"

int g_exit_code = -1;
static pthread_t g_main_thread = -1;

static PyObject *SpotifyError;

static PyObject *SpotifyApiVersion;

typedef struct {
    PyObject_HEAD
    void *_session;
} Session;

static void Session_dealloc(Session *self) {
    Py_XDECREF(self->_session);
    self->ob_type->tp_free((PyObject *)self);
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
	g_exit_code = 5;
        return NULL;
    }
    g_exit_code = 0;
    fprintf(stderr, "Session_logout completing\n");
    return Py_BuildValue("");
};

static PyMethodDef Session_methods[] = {
    {"username", (PyCFunction)Session_username, METH_NOARGS, "Return the canonical username for the logged in user"},
    {"display_name", (PyCFunction)Session_display_name, METH_NOARGS, "Return the full name for the logged in user"},
    {"user_is_loaded", (PyCFunction)Session_user_is_loaded, METH_NOARGS, "Return whether the user is loaded or not"},
    {"logout", (PyCFunction)Session_logout, METH_NOARGS, "Logout from the session and terminate the main loop"},
    {NULL}
};

static PyTypeObject SessionType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_spotify.Session",             /*tp_name*/
    sizeof(Session),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Session_dealloc, /*tp_dealloc*/
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




static void logged_in(sp_session *session, sp_error error) {
    fprintf(stderr, "logged_in called\n");
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Session *psession = PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    fprintf(stderr, "client is %p\n", client);
    PyObject_CallMethod(client, "logged_in", "Oi", psession, error);
    PyGILState_Release(gstate);
}

static void logged_out(sp_session *session) {
    fprintf(stderr, "logged_out called\n");
}

static void metadata_updated(sp_session *session) {
    fprintf(stderr, "metadata_updated called\n");
}

static void connection_error(sp_session *session, sp_error error) {
    fprintf(stderr, "connection_error called\n");
}

static void message_to_user(sp_session *session, const char *message) {
}

static void notify_main_thread(sp_session *session) {
    fprintf(stderr, "notify_main_thread called\n");
    pthread_kill(g_main_thread, SIGIO);
}

static void music_delivery(sp_session *session, const sp_audioformat *format, const void *frames, int num_frames) {
    fprintf(stderr, "music_delivery called\n");
}

static void play_token_lost(sp_session *session) {
    fprintf(stderr, "play_token_lost called\n");
}

static void log_message(sp_session *session, const char *data) {
    fprintf(stderr, "log_message called: %s\n", data);
}

static void end_of_track(sp_session *session) {
    fprintf(stderr, "end_of_track called\n");
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

static void loop(sp_session *session) {
    sigset_t sigset;
    sigemptyset(&sigset);
    sigaddset(&sigset, SIGIO);
    while (g_exit_code < 0) {
	fprintf(stderr, "running event loop\n");
	int timeout = -1;
	pthread_sigmask(SIG_BLOCK, &sigset, NULL);
	sp_session_process_events(session, &timeout);
	pthread_sigmask(SIG_UNBLOCK, &sigset, NULL);
	fprintf(stderr, "sleeping for %d seconds\n", timeout/1000);
	usleep(timeout * 1000);
    }
}

static PyObject *spotify_run(PyObject *self, PyObject *args) {

    PyObject *client;
    if(!PyArg_ParseTuple(args, "O", &client))
	return NULL;
    Py_INCREF(client);

    fprintf(stderr, "client is %p\n", client);
    sp_session_config config;

    config.api_version = SPOTIFY_API_VERSION;
    config.userdata = (void *)client;

    PyObject *cache_location = PyObject_GetAttr(client, PyString_FromString("cache_location"));
    if(cache_location == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a cache_location");
        return NULL;
    }
    config.cache_location = PyString_AsString(cache_location);

    PyObject *settings_location = PyObject_GetAttr(client, PyString_FromString("settings_location"));
    if(settings_location == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a settings_location");
        return NULL;
    }
    config.settings_location = PyString_AsString(settings_location);

    PyObject *application_key = PyObject_GetAttr(client, PyString_FromString("application_key"));
    if(application_key == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide an application_key");
        return NULL;
    }
    config.application_key = PyString_AsString(application_key);
    config.application_key_size = PyString_Size(application_key);

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

    uobj = PyObject_GetAttr(client, PyString_FromString("username"));
    if(uobj == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a username");
	return NULL;
    }
    username = PyString_AsString(uobj);

    pobj = PyObject_GetAttr(client, PyString_FromString("password"));
    if(pobj == NULL) {
	PyErr_SetString(SpotifyError, "Client did not provide a password");
	return NULL;
    }
    password = PyString_AsString(pobj);

    error = sp_session_init(&config, &session);
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }
    error = sp_session_login(session, username, password);
    if(error != SP_ERROR_OK) {
	PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }

    fprintf(stderr, "Entering main loop\n");
    loop(session);
    return Py_BuildValue("");
}

static PyMethodDef module_methods[] = {
    {"run", spotify_run, METH_VARARGS, "Run the spotify subsystem.  this will return on error, or after spotify is logged out."},
    {NULL, NULL, 0, NULL}
};

static void sigIgn(int signo) {
}

PyMODINIT_FUNC initsession(void) {
    PyObject *m;

    if(PyType_Ready(&SessionType) < 0)
	return;

    m = Py_InitModule("session", module_methods);
    if(m == NULL)
        return;

    SpotifyError = PyErr_NewException("spotify.session.error", NULL, NULL);
    Py_INCREF(SpotifyError);
    PyModule_AddObject(m, "error", SpotifyError);

    SpotifyApiVersion = Py_BuildValue("i", SPOTIFY_API_VERSION);
    Py_INCREF(SpotifyApiVersion);
    PyModule_AddObject(m, "api_version", SpotifyApiVersion);

    g_main_thread = pthread_self();
    signal(SIGIO, &sigIgn);

    PyModule_AddObject(m, "Session", (PyObject *)&SessionType);
}

PyMODINIT_FUNC initmocksession(void) {
    PyObject *m;

    if(PyType_Ready(&SessionType) < 0)
	return;

    m = Py_InitModule("mocksession", module_methods);
    if(m == NULL)
        return;

    SpotifyError = PyErr_NewException("spotify.session.error", NULL, NULL);
    Py_INCREF(SpotifyError);
    PyModule_AddObject(m, "error", SpotifyError);

    SpotifyApiVersion = Py_BuildValue("i", SPOTIFY_API_VERSION);
    Py_INCREF(SpotifyApiVersion);
    PyModule_AddObject(m, "api_version", SpotifyApiVersion);

    g_main_thread = pthread_self();
    signal(SIGIO, &sigIgn);

    PyModule_AddObject(m, "Session", (PyObject *)&SessionType);
}
