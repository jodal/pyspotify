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
#include "user.h"

static int session_constructed = 0;
sp_session *g_session;

static PyObject *
Session_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    Session *self;

    self = (Session *) type->tp_alloc(type, 0);
    self->_session = NULL;
    return (PyObject *)self;
}

PyObject *
Session_FromSpotify(sp_session * session)
{
    PyObject *s = PyObject_CallObject((PyObject *)&SessionType, NULL);

    ((Session *) s)->_session = session;
    return s;
}

static PyMemberDef Session_members[] = {
    {NULL}
};

static PyObject *
Session_username(Session * self)
{
    sp_user *user;

    user = sp_session_user(self->_session);
    if (user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    const char *username = sp_user_canonical_name(user);

    return PyUnicode_FromString(username);
};

static PyObject *
Session_display_name(Session * self)
{
    sp_user *user;

    user = sp_session_user(self->_session);
    if (user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    const char *username = sp_user_display_name(user);

    return PyUnicode_FromString(username);
};

static PyObject *
Session_user_is_loaded(Session * self)
{
    sp_user *user;

    user = sp_session_user(self->_session);
    if (user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    bool loaded = sp_user_is_loaded(user);

    return Py_BuildValue("i", loaded);
};

static PyObject *
Session_logout(Session * self)
{
    Py_BEGIN_ALLOW_THREADS;
    sp_session_logout(self->_session);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
};

PyObject *
handle_error(int err)
{
    if (err != 0) {
        PyErr_SetString(SpotifyError, sp_error_message(err));
        return NULL;
    }
    else {
        Py_RETURN_NONE;
    }
}

static PyObject *
Session_playlist_container(Session * self)
{
    sp_playlistcontainer *pc;

    Py_BEGIN_ALLOW_THREADS;
    pc = sp_session_playlistcontainer(self->_session);
    Py_END_ALLOW_THREADS;

    PlaylistContainer *ppc =
        (PlaylistContainer *) PyObject_CallObject((PyObject *)
                                                  &PlaylistContainerType,
                                                  NULL);

    ppc->_playlistcontainer = pc;
    sp_playlistcontainer_add_ref(pc);
    return (PyObject *)ppc;
}

static PyObject *
Session_load(Session * self, PyObject *args)
{
    Track *track;
    sp_track *t;
    sp_session *s;
    sp_error err;

    if (!PyArg_ParseTuple(args, "O!", &TrackType, &track)) {
        return NULL;
    }
    t = track->_track;
    s = self->_session;

    Py_BEGIN_ALLOW_THREADS;
    err = sp_session_player_load(s, t);
    Py_END_ALLOW_THREADS;

    return handle_error(err);
}

static PyObject *
Session_seek(Session * self, PyObject *args)
{
    int seek;

    if (!PyArg_ParseTuple(args, "i", &seek))
        return NULL;

    Py_BEGIN_ALLOW_THREADS;
    sp_session_player_seek(self->_session, seek);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

static PyObject *
Session_play(Session * self, PyObject *args)
{
    int play;

    if (!PyArg_ParseTuple(args, "i", &play))
        return NULL;

    Py_BEGIN_ALLOW_THREADS;
    sp_session_player_play(self->_session, play);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

static PyObject *
Session_unload(Session * self)
{
    sp_session_player_unload(self->_session);
    Py_RETURN_NONE;
}

static PyObject *
Session_process_events(Session * self)
{
    int timeout;

    Py_BEGIN_ALLOW_THREADS;
    sp_session_process_events(self->_session, &timeout);
    Py_END_ALLOW_THREADS;

    return Py_BuildValue("i", timeout);
}

void
search_complete(sp_search * search, Callback * st)
{
    PyObject *res, *results;
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    results = Results_FromSpotify(search);
    res = PyObject_CallFunctionObjArgs(st->callback, results, st->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(st->callback);
    delete_trampoline(st);
    Py_XDECREF(res);
    Py_DECREF(results);
    PyGILState_Release(gstate);
}

static PyObject *
Session_search(Session * self, PyObject *args, PyObject *kwds)
{
    char *query;
    sp_search *search;
    PyObject *callback, *userdata = NULL;
    int track_offset = 0, track_count = 32,
        album_offset = 0, album_count = 32, artist_offset = 0, artist_count =
        32, playlist_offset = 0, playlist_count = 32;
    Callback *st;
    PyObject *results;
    sp_search_type search_type = SP_SEARCH_STANDARD;
    char *str_search_type = NULL;

    static char *kwlist[] = { "query", "callback",
        "track_offset", "track_count",
        "album_offset", "album_count",
        "artist_offset", "artist_count",
        "playlist_offset", "playlist_count",
        "search_type", "userdata", NULL
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO|iiiiiiiisO", kwlist,
                                     ENCODING, &query, &callback,
                                     &track_offset, &track_count,
                                     &album_offset, &album_count,
                                     &artist_offset, &artist_count,
                                     &playlist_offset, &playlist_count,
                                     &str_search_type, &userdata))
        return NULL;
    /* Determine search type */
    if (str_search_type) {
        if (strcmp(str_search_type, "standard") == 0) {} // default
        else if (strcmp(str_search_type, "suggest") == 0) {
            search_type = SP_SEARCH_SUGGEST;
        }
        else {
            PyErr_Format(SpotifyError, "Unknown search type: %s", str_search_type);
            return NULL;
        }
    }
    if (!userdata)
        userdata = Py_None;
    st = create_trampoline(callback, NULL, userdata);

    Py_BEGIN_ALLOW_THREADS;
    search = sp_search_create(self->_session, query,
                              track_offset, track_count,
                              album_offset, album_count,
                              artist_offset, artist_count,
                              playlist_offset, playlist_count,
                              search_type,
                              (search_complete_cb *) search_complete,
                              (void *)st);
    Py_END_ALLOW_THREADS;

    results = Results_FromSpotify(search);
    return results;
}

static PyObject *
Session_browse_album(Session * self, PyObject *args, PyObject *kwds)
{
    /* Deprecated, calls the AlbumBrowserType object */
    PyObject *result =
        PyObject_Call((PyObject *)&AlbumBrowserType, args, kwds);
    return result;
}

static PyObject *
Session_browse_artist(Session * self, PyObject *args, PyObject *kwds)
{
    /* Deprecated, calls the ArtistBrowserType object */
    PyObject *result =
        PyObject_Call((PyObject *)&ArtistBrowserType, args, kwds);
    return result;
}

static PyObject *
Session_image_create(Session * self, PyObject *args)
{
    byte *image_id;
    size_t len;
    sp_image *image;

    if (!PyArg_ParseTuple(args, "s#", &image_id, &len))
        return NULL;
    if (len != 20) {
        PyErr_SetString(SpotifyError, "Image id length != 20");
        return NULL;
    }
    image = sp_image_create(self->_session, image_id);
    return Image_FromSpotify(image);
}

static PyObject *
Session_set_preferred_bitrate(Session * self, PyObject *args)
{
    int bitrate;

    if (!PyArg_ParseTuple(args, "i", &bitrate))
        return NULL;

    Py_BEGIN_ALLOW_THREADS;
    sp_session_preferred_bitrate(self->_session, bitrate);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

static PyObject *
Session_starred(Session * self)
{
    sp_playlist *spl;

    Py_BEGIN_ALLOW_THREADS;
    spl = sp_session_starred_create(self->_session);
    Py_END_ALLOW_THREADS;

    PyObject *pl = Playlist_FromSpotify(spl);

    return pl;
}

static PyObject *
Session_flush_caches(Session * self)
{
    Py_BEGIN_ALLOW_THREADS;
    sp_session_flush_caches(self->_session);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

static PyMethodDef Session_methods[] = {
    {"username", (PyCFunction)Session_username, METH_NOARGS,
     "Return the canonical username for the logged in user"},
    {"display_name", (PyCFunction)Session_display_name, METH_NOARGS,
     "Return the full name for the logged in user"},
    {"user_is_loaded", (PyCFunction)Session_user_is_loaded, METH_NOARGS,
     "Return whether the user is loaded or not"},
    {"logout", (PyCFunction)Session_logout, METH_NOARGS,
     "Logout from the session and terminate the main loop"},
    {"process_events", (PyCFunction)Session_process_events, METH_NOARGS,
     "Process any outstanding events"},
    {"load", (PyCFunction)Session_load, METH_VARARGS,
     "Load the specified track on the player"},
    {"seek", (PyCFunction)Session_seek, METH_VARARGS,
     "Seek the currently loaded track"},
    {"play", (PyCFunction)Session_play, METH_VARARGS,
     "Play or pause the currently loaded track"},
    {"unload", (PyCFunction)Session_unload, METH_NOARGS,
     "Stop the currently playing track"},
    {"playlist_container", (PyCFunction)Session_playlist_container,
     METH_NOARGS,
     "Return the playlist container for the currently logged in user"},
    {"browse_album", (PyCFunction)Session_browse_album,
     METH_VARARGS | METH_KEYWORDS,
     "Browse an album, calling the callback when the browse request completes"},
    {"browse_artist", (PyCFunction)Session_browse_artist,
     METH_VARARGS | METH_KEYWORDS,
     "Browse an artist, calling the callback when the browse request completes"},
    {"search", (PyCFunction)Session_search, METH_VARARGS | METH_KEYWORDS,
     "Conduct a search, calling the callback when results are available"},
    {"image_create", (PyCFunction)Session_image_create, METH_VARARGS,
     "Create an image of album cover art"},
    {"set_preferred_bitrate", (PyCFunction)Session_set_preferred_bitrate,
     METH_VARARGS,
     "Set the preferred bitrate of the audio stream. 0 = 160k, 1 = 320k"},
    {"starred", (PyCFunction)Session_starred, METH_NOARGS,
     "Get the starred playlist for the logged in user"},
    {"flush_caches", (PyCFunction)Session_flush_caches, METH_NOARGS,
     "Flush the libspotify caches"},
    {NULL}
};

PyTypeObject SessionType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.Session", /*tp_name */
    sizeof(Session),    /*tp_basicsize */
    0,                  /*tp_itemsize */
    0,                  /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    0,                  /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    0,                  /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "Session objects",  /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    Session_methods,    /* tp_methods */
    Session_members,    /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    Session_new         /* tp_new */
};

/*************************************/
/*           CALLBACK SHIMS          */
/*************************************/

static void
logged_in(sp_session * session, sp_error error)
{
    PyGILState_STATE gstate;
    PyObject *res, *err, *method;

#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-session- >> logged_in called\n");
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    err = error_message(error);
    method = PyObject_GetAttrString(client, "logged_in");
    res = PyObject_CallFunctionObjArgs(method, psession, err, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_DECREF(err);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
logged_out(sp_session * session)
{
    PyGILState_STATE gstate;
    PyObject *res, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> logged_out called\n");
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    method = PyObject_GetAttrString(client, "logged_out");
    res = PyObject_CallFunctionObjArgs(method, psession, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
metadata_updated(sp_session * session)
{
    PyGILState_STATE gstate;
    PyObject *res, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> metadata_updated called\n");
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    method = PyObject_GetAttrString(client, "metadata_updated");
    res = PyObject_CallFunctionObjArgs(method, psession, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
connection_error(sp_session * session, sp_error error)
{
    PyGILState_STATE gstate;
    PyObject *res, *err, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> connection_error called\n");
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    err = error_message(error);
    method = PyObject_GetAttrString(client, "connection_error");
    res = PyObject_CallFunctionObjArgs(method, psession, err, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_DECREF(err);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
message_to_user(sp_session * session, const char *message)
{
    PyGILState_STATE gstate;
    PyObject *res, *method, *msg;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> message to user: %s\n", message);
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    msg = PyUnicode_FromString(message);
    method = PyObject_GetAttrString(client, "message_to_user");
    res =
        PyObject_CallFunctionObjArgs(method, psession, msg, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
notify_main_thread(sp_session * session)
{
    PyGILState_STATE gstate;
    PyObject *res, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> notify_main_thread called\n");
#endif
    if (!session_constructed)
        return;
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    if (client != NULL) {
        method = PyObject_GetAttrString(client, "notify_main_thread");
        res = PyObject_CallFunctionObjArgs(method, psession, NULL);
        if (!res)
            PyErr_WriteUnraisable(method);
        Py_XDECREF(res);
        Py_DECREF(method);
    }
    Py_DECREF(psession);
    PyGILState_Release(gstate);
}

static int
frame_size(const sp_audioformat * format)
{
    switch (format->sample_type) {
    case SP_SAMPLETYPE_INT16_NATIVE_ENDIAN:
        return format->channels * 2;    // 16 bits = 2 bytes
        break;
    default:
        return -1;
    }
}

static int
music_delivery(sp_session * session, const sp_audioformat * format,
               const void *frames, int num_frames)
{
    PyGILState_STATE gstate;
    PyObject *res, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> music_delivery called\n");
#endif
    gstate = PyGILState_Ensure();
    int siz = frame_size(format);
    PyObject *pyframes = PyBuffer_FromMemory((void *)frames, num_frames * siz);
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);
    method = PyObject_GetAttrString(client, "music_delivery");
    res =
        PyObject_CallFunction(method, "OOiiiii", psession,
                              pyframes, siz, num_frames, format->sample_type,
                              format->sample_rate, format->channels);
    int consumed = num_frames;  // assume all consumed
    if (!res)
        PyErr_WriteUnraisable(method);
    else if (PyInt_Check(res))
        consumed = (int)PyInt_AsLong(res);
    else if (PyLong_Check(res))
        consumed = (int)PyLong_AsLong(res);
    else {
        PyErr_SetString(PyExc_TypeError,
                        "music_delivery must return an integer");
        PyErr_WriteUnraisable(method);
    }
    Py_DECREF(pyframes);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
    return consumed;
}

static void
play_token_lost(sp_session * session)
{
    PyGILState_STATE gstate;
    PyObject *res, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> play_token_lost called\n");
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    method = PyObject_GetAttrString(client, "play_token_lost");
    res = PyObject_CallFunctionObjArgs(method, psession, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
log_message(sp_session * session, const char *data)
{
    PyGILState_STATE gstate;
    PyObject *res, *method, *msg;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> log message: %s\n", data);
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    msg = PyUnicode_FromString(data);
    method = PyObject_GetAttrString(client, "log_message");
    res = PyObject_CallFunctionObjArgs(method, psession, msg, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(msg);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
end_of_track(sp_session * session)
{
    PyGILState_STATE gstate;
    PyObject *res, *method;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> end_of_track called\n");
#endif
    gstate = PyGILState_Ensure();
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    PyObject *client = (PyObject *)sp_session_userdata(session);

    method = PyObject_GetAttrString(client, "end_of_track");
    res = PyObject_CallFunctionObjArgs(method, psession, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(psession);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

static void
credentials_blob_updated(sp_session *session, const char *blob)
{
    PyGILState_STATE gstate;
    PyObject *res, *method, *client, *py_session, *py_blob;

#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- >> credentials_blob_updated called\n");
#endif
    gstate = PyGILState_Ensure();
    client = (PyObject *)sp_session_userdata(session);
    py_session = Session_FromSpotify(session);
    py_blob = PyBytes_FromString(blob);

    method = PyObject_GetAttrString(client, "credentials_blob_updated");
    res = PyObject_CallFunctionObjArgs(method, py_session, py_blob, NULL);
    if (!res)
        PyErr_WriteUnraisable(method);
    Py_DECREF(py_session);
    Py_DECREF(py_blob);
    Py_XDECREF(res);
    Py_DECREF(method);
    PyGILState_Release(gstate);
}

void
session_init(PyObject *m)
{
    Py_INCREF(&SessionType);
    PyModule_AddObject(m, "Session", (PyObject *)&SessionType);
}

char *
PySpotify_GetConfigString(PyObject *client, const char *attr, bool optional)
{
    PyObject *py_value, *py_uvalue;
    char *value;

    py_value = PyObject_GetAttrString(client, attr);
    if (!py_value || py_value == Py_None) {
        if (optional) {
            return (char *)-1;
        }
        else {
            PyErr_Format(SpotifyError, "%s not set", attr);
            return NULL;
        }
    }
    if (PyUnicode_Check(py_value)) {
        py_uvalue = py_value;
        py_value = PyUnicode_AsEncodedString(py_uvalue, ENCODING, "replace");
        Py_DECREF(py_uvalue);
    }
    else if (!PyBytes_Check(py_value)) {
        PyErr_Format(SpotifyError,
                     "configuration value '%s' must be a string/unicode object",
                     attr);
        return NULL;
    }
    value = PyMem_Malloc(strlen(PyBytes_AS_STRING(py_value)) + 1);
    strcpy(value, PyBytes_AS_STRING(py_value));
    Py_DECREF(py_value);
    return value;
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
    &end_of_track,
    NULL, /* streaming_error */
    NULL, /* userinfo_updated */
    NULL, /* start_playback */
    NULL, /* stop_playback */
    NULL, /* get_audio_buffer_stats */
    NULL, /* offline_status_updated */
    NULL, /* offline_error */
    &credentials_blob_updated,
};

PyObject *
session_connect(PyObject *self, PyObject *args)
{
    sp_session_config config;
    PyObject *client;
    sp_session *session;
    sp_error error;
    char *username, *password;
    char *cache_location, *settings_location, *user_agent;
    bool relogin = 0, remember_me;
    char *blob = NULL;

    if (!PyArg_ParseTuple(args, "O", &client))
        return NULL;
    PyEval_InitThreads();

    memset(&config, 0, sizeof(config));
    config.api_version = SPOTIFY_API_VERSION;
    config.userdata = (void *)client;
    config.callbacks = &g_callbacks;

    cache_location = PySpotify_GetConfigString(client, "cache_location", 0);
    if (!cache_location)
        return NULL;
    config.cache_location = cache_location;
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-session- Cache location is '%s'\n",
            cache_location);
#endif

    settings_location = PySpotify_GetConfigString(client,
                                                  "settings_location", 0);
    config.settings_location = settings_location;
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-session- Settings location is '%s'\n",
            settings_location);
#endif

    PyObject *application_key =
        PyObject_GetAttr(client, PyBytes_FromString("application_key"));
    if (!application_key) {
        PyErr_SetString(SpotifyError,
                        "application_key not set");
        return NULL;
    }
    else if (!PyBytes_Check(application_key)) {
        PyErr_SetString(SpotifyError,
                        "application_key must be a byte string");
        return NULL;
    }
    char *s_appkey;
    Py_ssize_t l_appkey;

    PyBytes_AsStringAndSize(application_key, &s_appkey, &l_appkey);
    config.application_key_size = l_appkey;
    config.application_key = PyMem_Malloc(l_appkey);
    memcpy((char *)config.application_key, s_appkey, l_appkey);

    user_agent = PySpotify_GetConfigString(client, "user_agent", 0);
    if (!user_agent)
        return NULL;
    if (strlen(user_agent) > 255) {
        PyErr_SetString(SpotifyError, "user agent must be 255 characters max");
        return NULL;
    }
    config.user_agent = user_agent;
#ifdef DEBUG
        fprintf(stderr, "[DEBUG]-session- User agent set to '%s'\n",
                            user_agent);
#endif
    username = PySpotify_GetConfigString(client, "username", 1);
    if (!username)
        return NULL;

    password = PySpotify_GetConfigString(client, "password", 1);
    if (!password)
        return NULL;

    if ((long) username < 0 || (long) password < 0)
        relogin = 1;

    PyObject *remember = PyObject_GetAttr(client, PyBytes_FromString("remember_me"));
    remember_me = (remember == Py_True);
    PyErr_Clear();
    Py_XDECREF(remember);

    /* Binary blob to use in place of a password */
    PyObject *py_blob = PyObject_GetAttr(client, PyBytes_FromString("login_blob"));
    if (py_blob != NULL) {
        if (!(PyBytes_Check(py_blob))) {
            PyErr_SetString(SpotifyError, "login_blob must be a string of bytes.");
            Py_XDECREF(py_blob);
            return NULL;
        }
        blob = PyString_AS_STRING(py_blob);
        /* if blob is the empty string (= default value), we pass NULL to
         * sp_session_login */
        if (blob[0] == '\0')
            blob = NULL;
    } else {
        PyErr_Clear();
    }

#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-session- creating session...\n");
#endif
    error = sp_session_create(&config, &session);
    if (error != SP_ERROR_OK) {
        PyErr_SetString(SpotifyError, sp_error_message(error));
        Py_XDECREF(py_blob);
        return NULL;
    }
    session_constructed = 1;

    if (relogin) {
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-session- relogin in progress...\n");
#endif
        error = sp_session_relogin(session);
        if (error != SP_ERROR_OK) {
            PyErr_SetString(SpotifyError, sp_error_message(error));
            Py_XDECREF(py_blob);
            return NULL;
        }
    } else {
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-session- login as %s in progress...\n",
            username);
#endif
        Py_BEGIN_ALLOW_THREADS;
        sp_session_login(session, username, password, remember_me, blob);
        Py_END_ALLOW_THREADS;
    }
    Py_XDECREF(py_blob);
    g_session = session;
    Session *psession =
        (Session *) PyObject_CallObject((PyObject *)&SessionType, NULL);
    psession->_session = session;
    return (PyObject *)psession;
}
