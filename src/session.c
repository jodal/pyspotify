#include <Python.h>
#include <structmember.h>
#include <libgen.h>
#include <unistd.h>
#include <stdint.h>
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

/* TODO: is this safe as just an int, or should it be a condition variable? */
static int session_constructed = 0;

/* TODO: we probably should have a lock protecting access to this */
/* TODO: more or less all use of Session_SP_SESSION(self) could just be g_session... */
sp_session *g_session;

static sp_session *
create_session(PyObject *client, PyObject *settings);

static void
session_callback(sp_session *session, const char *attr, PyObject *extra);

static PyObject *
Session_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Session_SP_SESSION(self) = NULL;
    return self;
}

PyObject *
Session_FromSpotify(sp_session *session)
{
    PyObject *self = SessionType.tp_alloc(&SessionType, 0);
    Session_SP_SESSION(self) = session;
    return self;
}

static PyObject *
Session_create(PyTypeObject *type, PyObject *args)
{
    PyObject *client, *settings;
    if (!PyArg_ParseTuple(args, "OO", &client, &settings))
        return NULL;

    PyEval_InitThreads();
    sp_session *session = create_session(client, settings);
    if (session == NULL)
        return NULL;
    return Session_FromSpotify(session);
}

static PyObject *
Session_username(PyObject *self)
{
    sp_user *user = sp_session_user(Session_SP_SESSION(self));
    if (user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    return PyUnicode_FromString(sp_user_canonical_name(user));
};

static PyObject *
Session_display_name(PyObject *self)
{
    sp_user *user = sp_session_user(Session_SP_SESSION(self));
    if (user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    return PyUnicode_FromString(sp_user_display_name(user));
};

static PyObject *
Session_user_is_loaded(PyObject *self)
{
    sp_user *user = sp_session_user(Session_SP_SESSION(self));
    if (user == NULL) {
        PyErr_SetString(SpotifyError, "Not logged in");
        return NULL;
    }
    return PyBool_FromLong(sp_user_is_loaded(user));
};

static PyObject *
Session_logout(PyObject *self)
{
    Py_BEGIN_ALLOW_THREADS;
    sp_session_logout(Session_SP_SESSION(self));
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
};

static PyObject *
Session_playlist_container(PyObject *self)
{
    sp_playlistcontainer *container;

    Py_BEGIN_ALLOW_THREADS;
    container = sp_session_playlistcontainer(Session_SP_SESSION(self));
    Py_END_ALLOW_THREADS;

    return PlaylistContainer_FromSpotify(container);
}

static PyObject *
Session_load(PyObject *self, PyObject *args)
{
    PyObject *track;
    sp_error error;

    if (!PyArg_ParseTuple(args, "O!", &TrackType, &track))
        return NULL;

    Py_BEGIN_ALLOW_THREADS;
    error = sp_session_player_load(Session_SP_SESSION(self), Track_SP_TRACK(track));
    Py_END_ALLOW_THREADS;

    return none_or_raise_error(error);
}

static PyObject *
Session_seek(PyObject *self, PyObject *args)
{
    int seek;
    sp_error error;

    if (!PyArg_ParseTuple(args, "i", &seek))
        return NULL;

    Py_BEGIN_ALLOW_THREADS;
    error = sp_session_player_seek(Session_SP_SESSION(self), seek);
    Py_END_ALLOW_THREADS;

    return none_or_raise_error(error);
}

static PyObject *
Session_play(PyObject *self, PyObject *args)
{
    int play;

    /* TODO: Expect bool or something that can be coerced into one? */
    if (!PyArg_ParseTuple(args, "i", &play))
        return NULL;

    Py_BEGIN_ALLOW_THREADS;
    sp_session_player_play(Session_SP_SESSION(self), play);
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

static PyObject *
Session_unload(PyObject *self)
{
    sp_session_player_unload(Session_SP_SESSION(self));
    Py_RETURN_NONE;
}

static PyObject *
Session_process_events(PyObject *self)
{
    int timeout;

    Py_BEGIN_ALLOW_THREADS;
    sp_session_process_events(Session_SP_SESSION(self), &timeout);
    Py_END_ALLOW_THREADS;

    return Py_BuildValue("i", timeout);
}

void
Session_search_complete(sp_search *search, void *data)
{
    Callback *trampoline = (Callback *)data;
    debug_printf("browse complete (%p, %p)", search, trampoline);

    if (trampoline == NULL)
        return;

    PyObject *result, *search_results;
    PyGILState_STATE gstate = PyGILState_Ensure();

    search_results = Results_FromSpotify(search);
    if (search_results != NULL) {
        result = PyObject_CallFunctionObjArgs(trampoline->callback, search_results,
                                              trampoline->userdata, NULL);
        if (result == NULL)
            PyErr_WriteUnraisable(trampoline->callback);
        else
            Py_DECREF(result);
        Py_DECREF(search_results);
    }
    delete_trampoline(trampoline);
    PyGILState_Release(gstate);
}

static PyObject *
Session_search(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *callback, *userdata = NULL;
    Callback *trampoline;

    char *query, *tmp;
    sp_search *search;
    sp_search_type search_type = SP_SEARCH_STANDARD;

    int track_offset = 0, track_count = 32, album_offset = 0, album_count = 32,
        artist_offset = 0, artist_count = 32, playlist_offset = 0,
        playlist_count = 32;

    static char *kwlist[] = {
        "query", "callback", "track_offset", "track_count", "album_offset",
        "album_count", "artist_offset", "artist_count", "playlist_offset",
        "playlist_count", "search_type", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO|iiiiiiiisO", kwlist,
                                     ENCODING, &query, &callback,
                                     &track_offset, &track_count,
                                     &album_offset, &album_count,
                                     &artist_offset, &artist_count,
                                     &playlist_offset, &playlist_count,
                                     &tmp, &userdata))
        return NULL;

    /* TODO: create type string constants. */
    /* TODO: extract to helper */
    if (tmp) {
        if (strcmp(tmp, "standard") == 0) {
        }
        else if (strcmp(tmp, "suggest") == 0) {
            search_type = SP_SEARCH_SUGGEST;
        }
        else {
            PyErr_Format(SpotifyError, "Unknown search type: %s", tmp);
            return NULL;
        }
    }

    trampoline = create_trampoline(callback, userdata);

    Py_BEGIN_ALLOW_THREADS;
    /* TODO: audit that we cleanup with _release */
    search = sp_search_create(Session_SP_SESSION(self), query, track_offset,
                              track_count, album_offset, album_count,
                              artist_offset, artist_count, playlist_offset,
                              playlist_count, search_type,
                              Session_search_complete, (void *)trampoline);
    Py_END_ALLOW_THREADS;

    /* TODO: this leaks a ref */
    return Results_FromSpotify(search);
}

static PyObject *
Session_browse_album(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyErr_Warn(PyExc_DeprecationWarning, "use the album browser directly.");
    return PyObject_Call((PyObject *)&AlbumBrowserType, args, kwds);
}

static PyObject *
Session_browse_artist(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyErr_Warn(PyExc_DeprecationWarning, "use the artist browser directly.");
    return PyObject_Call((PyObject *)&ArtistBrowserType, args, kwds);
}

static PyObject *
Session_image_create(PyObject *self, PyObject *args)
{
    byte *image_id;
    size_t len;
    sp_image *image;

    if (!PyArg_ParseTuple(args, "s#", &image_id, &len))
        return NULL;
    if ((int)len != 20) {
        PyErr_SetString(SpotifyError, "Image id length != 20");
        return NULL;
    }

    /* TODO: audit that we cleanup with _release */
    image = sp_image_create(Session_SP_SESSION(self), image_id);
    /* TODO: this leaks a ref */
    return Image_FromSpotify(image);
}

static PyObject *
Session_set_preferred_bitrate(PyObject *self, PyObject *args)
{
    int bitrate;

    if (!PyArg_ParseTuple(args, "i", &bitrate))
        return NULL;

    sp_session_preferred_bitrate(Session_SP_SESSION(self), bitrate);
    Py_RETURN_NONE;
}

static PyObject *
Session_starred(PyObject *self)
{
    sp_playlist *playlist;

    Py_BEGIN_ALLOW_THREADS;
    /* TODO: audit that we cleanup with _release */
    playlist  = sp_session_starred_create(Session_SP_SESSION(self));
    Py_END_ALLOW_THREADS;

    /* TODO: this leaks a ref */
    return Playlist_FromSpotify(playlist);
}

static PyObject *
Session_flush_caches(PyObject *self)
{
    Py_BEGIN_ALLOW_THREADS;
    sp_session_flush_caches(Session_SP_SESSION(self));
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

static PyObject *
Session_login(PyObject *self, PyObject *args, PyObject *kwds)
{
    char *username, *password = NULL, *blob = NULL;
    int remember_me = 1;

    sp_error error;

    static char *kwlist[] = {"username", "password", "remember_me", "blob",
                             NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "es|esiz", kwlist,
                                     ENCODING, &username, ENCODING, &password,
                                     &remember_me, &blob))
        return NULL;

    if ((!password) && (!blob)) {
        PyErr_SetString(SpotifyError, "one of the password or login blob " \
                        "is required to login");
        return NULL;
    }

    debug_printf("login as %s in progress...", username);

    Py_BEGIN_ALLOW_THREADS;
    error = sp_session_login(Session_SP_SESSION(self), username, password,
                             remember_me, blob);
    Py_END_ALLOW_THREADS;

    return none_or_raise_error(error);
}

static PyObject *
Session_relogin(PyObject *self)
{
    debug_printf("relogin in progress...");
    sp_error error = sp_session_relogin(Session_SP_SESSION(self));
    return none_or_raise_error(error);
}

static PyMethodDef Session_methods[] = {
    {"create",   (PyCFunction)Session_create, METH_VARARGS | METH_CLASS,
     "Returns a Session object embedding a newly created Spotify session"
    },
    {"username", (PyCFunction)Session_username, METH_NOARGS,
     "Return the canonical username for the logged in user"
    },
    {"display_name", (PyCFunction)Session_display_name, METH_NOARGS,
     "Return the full name for the logged in user"
    },
    {"user_is_loaded", (PyCFunction)Session_user_is_loaded, METH_NOARGS,
     "Return whether the user is loaded or not"
    },
    {"logout", (PyCFunction)Session_logout, METH_NOARGS,
     "Logs out the user from the Spotify service"
    },
    {"process_events", (PyCFunction)Session_process_events, METH_NOARGS,
     "Process any outstanding events"
    },
    {"load", (PyCFunction)Session_load, METH_VARARGS,
     "Load the specified track on the player"
    },
    {"seek", (PyCFunction)Session_seek, METH_VARARGS,
     "Seek the currently loaded track"
    },
    {"play", (PyCFunction)Session_play, METH_VARARGS,
     "Play or pause the currently loaded track"
    },
    {"unload", (PyCFunction)Session_unload, METH_NOARGS,
     "Stop the currently playing track"
    },
    {"playlist_container", (PyCFunction)Session_playlist_container, METH_NOARGS,
     "Return the playlist container for the currently logged in user"
    },
    {"browse_album", (PyCFunction)Session_browse_album, METH_VARARGS | METH_KEYWORDS,
     "Browse an album, calling the callback when the browse request completes"
    },
    {"browse_artist", (PyCFunction)Session_browse_artist, METH_VARARGS | METH_KEYWORDS,
     "Browse an artist, calling the callback when the browse request completes"
    },
    {"search", (PyCFunction)Session_search, METH_VARARGS | METH_KEYWORDS,
     "Conduct a search, calling the callback when results are available"
    },
    {"image_create", (PyCFunction)Session_image_create, METH_VARARGS,
     "Create an image of album cover art"
    },
    {"set_preferred_bitrate", (PyCFunction)Session_set_preferred_bitrate, METH_VARARGS,
     "Set the preferred bitrate of the audio stream. 0 = 160k, 1 = 320k"
    },
    {"starred", (PyCFunction)Session_starred, METH_NOARGS,
     "Get the starred playlist for the logged in user"
    },
    {"flush_caches", (PyCFunction)Session_flush_caches, METH_NOARGS,
     "Flush the libspotify caches"
    },
    {"login", (PyCFunction)Session_login, METH_VARARGS | METH_KEYWORDS,
     "Logs in the specified user to the Spotify service"
    },
    {"relogin", (PyCFunction)Session_relogin, METH_NOARGS,
     "Logs in the last user that logged in with the remember_me flag set"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Session_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject SessionType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Session",                        /*tp_name*/
    sizeof(Session),                          /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    0,                                        /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Session objects",                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Session_methods,                          /* tp_methods */
    Session_members,                          /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Session_new                               /* tp_new */
};

/*************************************/
/*           CALLBACK SHIMS          */
/*************************************/

/* TODO: convert to Py_VaBuildValue based solution so we can support
 *   music_delivery?
 * TODO: could we avoid having to pass session into the python callbacks, or
 *   could we at least store a g_py_session to save us reconstructing it all
 *   the time? Or would that break in unexpected ways if the session gets
 *   modified? Measuring the affect of changing say music_delivery to not
 *   waste time contructing the session would be a good place to start.
 * TODO: could we avoid having to lookup the attr for the callback on every
 *   single callback? Would that break cases where people change the config
 *   later, does that matter?
 */
static void
session_callback(sp_session * session, const char *attr, PyObject *extra)
{
    PyObject *callback, *client, *py_session, *result;
    py_session = Session_FromSpotify(session);
    if (py_session != NULL) {

        client = (PyObject *)sp_session_userdata(session);
        callback = PyObject_GetAttrString(client, attr);

        if (callback != NULL) {
            result = PyObject_CallFunctionObjArgs(callback, py_session, extra, NULL);

            if (result == NULL)
                PyErr_WriteUnraisable(callback);
            else
                Py_DECREF(result);

            Py_DECREF(callback);
        }
        Py_DECREF(py_session);
    }
}

static void
logged_in(sp_session * session, sp_error error)
{
    debug_printf(">> logged_in called: %s", sp_error_message(error));

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *py_error = error_message(error);
    if (py_error != NULL) {
        session_callback(session, "logged_in", py_error);
        Py_DECREF(py_error);
    }
    PyGILState_Release(gstate);
}

static void
logged_out(sp_session * session)
{
    debug_printf(">> logged_out called");

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    /* TODO: should this fallback to logged_out like old code did? */
    session_callback(session, "_manager_logged_out", NULL);
    PyGILState_Release(gstate);
}

static void
metadata_updated(sp_session * session)
{
    debug_printf(">> metadata_updated called");

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    session_callback(session, "metadata_updated", NULL);
    PyGILState_Release(gstate);
}

static void
connection_error(sp_session * session, sp_error error)
{
    debug_printf(">> connection_error called: %s", sp_error_message(error));

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *py_error = error_message(error);
    if (py_error != NULL) {
        session_callback(session, "connection_error", py_error);
        Py_DECREF(py_error);
    }
    PyGILState_Release(gstate);
}

static void
message_to_user(sp_session * session, const char *data)
{
    debug_printf(">> message_to_user called: %s", data);

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *message = PyUnicode_FromString(data);
    if (message != NULL) {
        session_callback(session, "message_to_user", message);
        Py_DECREF(message);
    }
    PyGILState_Release(gstate);
}

static void
notify_main_thread(sp_session * session)
{
    debug_printf(">> notify_main_thread called");

    if (!session_constructed)
        return;

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    session_callback(session, "notify_main_thread", NULL);
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
    /* TODO: This is called _all_ the time, make it faster? */

    // Note that we do not try to shoe horn this into session_callback as it is
    // quite different in that this needs to handle return values and much more
    // complicated arguments.

    debug_printf(">> music_delivery called: frames %d", num_frames);

    int consumed = num_frames;  // assume all consumed
    int size = frame_size(format);

    PyObject *callback, *client, *py_frames, *py_session, *result;
    PyGILState_STATE gstate = PyGILState_Ensure();

    /* TODO: check if session creations succeeds. */
    py_frames = PyBuffer_FromMemory((void *)frames, num_frames * size);
    py_session = Session_FromSpotify(session);

    /* TODO: check if callback get succeeds. */
    client = (PyObject *)sp_session_userdata(session);
    callback = PyObject_GetAttrString(client, "music_delivery");

    result = PyObject_CallFunction(callback, "OOiiiii", py_session, py_frames,
                                   size, num_frames, format->sample_type,
                                   format->sample_rate, format->channels);

    Py_XDECREF(py_frames);
    Py_XDECREF(py_session);

    if (result == NULL)
        PyErr_WriteUnraisable(callback);
    else {
        if (PyInt_Check(result))
            consumed = (int)PyInt_AsLong(result);
        else if (PyLong_Check(result))
            consumed = (int)PyLong_AsLong(result);
        else {
            PyErr_SetString(PyExc_TypeError,
                            "music_delivery must return an integer");
            PyErr_WriteUnraisable(callback);
        }
        Py_DECREF(result);
    }
    Py_XDECREF(callback);
    PyGILState_Release(gstate);
    return consumed;
}

static void
play_token_lost(sp_session * session)
{
    debug_printf(">> play_token_lost called");

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    session_callback(session, "play_token_lost", NULL);
    PyGILState_Release(gstate);
}

static void
log_message(sp_session * session, const char *data)
{
    debug_printf(">> log_message called: %s", data);

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *message = PyUnicode_FromString(data);
    if (message != NULL) {
        session_callback(session, "log_message", message);
        Py_DECREF(message);
    }
    PyGILState_Release(gstate);
}

static void
end_of_track(sp_session * session)
{
    debug_printf(">> end_of_track called");

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    session_callback(session, "end_of_track", NULL);
    PyGILState_Release(gstate);
}

static void
credentials_blob_updated(sp_session *session, const char *data)
{
    debug_printf(">> credentials_blob_updated called");

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *blob = PyBytes_FromString(data);
    if (blob != NULL) {
        session_callback(session, "credentials_blob_updated", blob);
        Py_DECREF(blob);
    }
    PyGILState_Release(gstate);
}

void
session_init(PyObject *module)
{
    Py_INCREF(&SessionType);
    PyModule_AddObject(module, "Session", (PyObject *)&SessionType);
}

static sp_session_callbacks g_callbacks = {
    &logged_in,                /* logged_in */
    &logged_out,               /* logged_out */
    &metadata_updated,         /* metadata_updated */
    &connection_error,         /* connection_error */
    &message_to_user,          /* message_to_user */
    &notify_main_thread,       /* notify_main_thread */
    &music_delivery,           /* music_delivery */
    &play_token_lost,          /* play_token_lost */
    &log_message,              /* log_message */
    &end_of_track,             /* end_of_track */
    NULL,                      /* streaming_error */
    NULL,                      /* userinfo_updated */
    NULL,                      /* start_playback */
    NULL,                      /* stop_playback */
    NULL,                      /* get_audio_buffer_stats */
    NULL,                      /* offline_status_updated */
    NULL,                      /* offline_error */
    &credentials_blob_updated, /* credentials_blob_updated */
};

// config_* functions are used as convenience wrappers to get
// data from the python attrs to the config objects. Setting the struct
// members without tmp intermediate would not work due to const char.
//
// Attribute not existing is a fatal error, as not being able to convert
// the attributes value. These cases _only_ set the python exception, so
// callers must check PyErr_Occurred().
static void
config_string(PyObject *instance, const char *attr, const char **target) {
    const char * tmp;
    PyObject *value = PyObject_GetAttrString(instance, attr);
    if (value == NULL) {
        PyErr_Format(SpotifyError, "%s not set", attr);
        return;
    }
    if (value != Py_None && PyArg_Parse(value, "es", ENCODING, &tmp))
        *target = tmp;
    Py_DECREF(value);
}

static void
config_data(PyObject *instance, const char *attr, const void **target, size_t *target_length) {
    int length;
    const void * tmp;
    PyObject *value = PyObject_GetAttrString(instance, attr);
    if (value == NULL) {
        PyErr_Format(SpotifyError, "%s not set", attr);
        return;
    }
    if (value != Py_None && PyArg_Parse(value, "s#", &tmp, &length)) {
        *target = tmp;
        *target_length = (size_t)length;
    }
    Py_DECREF(value);
}

static sp_session *
create_session(PyObject *client, PyObject *settings)
{
    sp_session_config config;
    sp_session* session;
    sp_error error;

    memset(&config, 0, sizeof(config));
    config.api_version = SPOTIFY_API_VERSION;
    config.userdata = (void*)client;
    config.callbacks = &g_callbacks;
    config.cache_location = "";
    config.user_agent = "pyspotify-fallback";

    config_data(settings, "application_key", &config.application_key, &config.application_key_size);
    config_string(settings, "cache_location", &config.cache_location);
    config_string(settings, "settings_location", &config.settings_location);
    config_string(settings, "user_agent", &config.user_agent);
    config_string(client, "proxy", &config.proxy);
    config_string(client, "proxy_username", &config.proxy_username);
    config_string(client, "proxy_password", &config.proxy_password);

    debug_printf("cache_location = %s", config.cache_location);
    debug_printf("settings_location = %s", config.settings_location);
    debug_printf("user_agent = %s", config.user_agent);
    debug_printf("proxy = %s", config.proxy);
    debug_printf("proxy_username = %s", config.proxy_username);
    debug_printf("proxy_password = %s", config.proxy_password);
    debug_printf("application_key_size = %zu", config.application_key_size);

    if (PyErr_Occurred() != NULL) {
        return NULL;
    }

    if (strlen(config.user_agent) > 255) {
        PyErr_SetString(SpotifyError, "user_agent may not be longer than 255.");
        return NULL;
    }

    if (config.application_key_size == 0) {
        PyErr_SetString(SpotifyError, "application_key must be provided.");
        return NULL;
    }

    debug_printf("creating session...");
    /* TODO: audit that we cleanup with _release */
    error = sp_session_create(&config, &session);
    if (error != SP_ERROR_OK) {
        PyErr_SetString(SpotifyError, sp_error_message(error));
        return NULL;
    }
    session_constructed = 1;
    g_session = session;
    return session;
}
