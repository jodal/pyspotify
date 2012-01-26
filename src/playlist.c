#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include "pyspotify.h"
#include "playlist.h"
#include "track.h"
#include "session.h"
#include "user.h"

/* This is the playlist callbacks table.
 *
 * It is a linked list of entries keeping enough information into pyspotify
 * to be able to remove the callbacks after a while, especially when dealing
 * with a different python Playlist object than the one the callbacks were
 * added from. Each entry corresponds to a spotify playlist on which
 * callbacks have been added. When all callbacks are removed from a playlist,
 * the entry is free'd from memory.
 */
static pl_cb_entry *playlist_callbacks_table = NULL;

static PyMemberDef Playlist_members[] = {
    {NULL}
};

static PyObject *
Playlist_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    Playlist *self;

    self = (Playlist *) type->tp_alloc(type, 0);
    self->_playlist = NULL;
    return (PyObject *)self;
}

PyObject *
Playlist_FromSpotify(sp_playlist * spl)
{
    Playlist *playlist =
        (Playlist *) PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    playlist->_playlist = spl;
    sp_playlist_add_ref(spl);
    sp_playlist_set_autolink_tracks(spl, 1);
    return (PyObject *)playlist;
}

static void
Playlist_dealloc(Playlist * self)
{
    if (self->_playlist)
        sp_playlist_release(self->_playlist);
    self->ob_type->tp_free(self);
}

static PyObject *
Playlist_is_loaded(Playlist * self)
{
    return Py_BuildValue("i", sp_playlist_is_loaded(self->_playlist));
}

static PyObject *
Playlist_remove_tracks(Playlist * self, PyObject *args)
{
    PyObject *py_tracks;
    PyObject *item;
    sp_error err;
    int *tracks;
    int num_tracks;
    int playlist_length;
    int i;

    if (!PyArg_ParseTuple(args, "O", &py_tracks))
        return NULL;
    if (!PySequence_Check(py_tracks)) {
        PyErr_SetString(PyExc_TypeError, "expected sequence");
        return NULL;
    }
    num_tracks = PySequence_Size(py_tracks);
    tracks = (int *)malloc(sizeof(tracks) * num_tracks);
    playlist_length = sp_playlist_num_tracks(self->_playlist);
    for (i = 0; i < num_tracks; i++) {
        item = PySequence_GetItem(py_tracks, i);
        if (!PyInt_Check(item)) {
            free(tracks);
            PyErr_SetString(PyExc_TypeError, "expected sequence of integers");
            return NULL;
        }
        tracks[i] = (int)PyInt_AsLong(item);
        if (tracks[i] > playlist_length) {
            PyErr_SetString(PyExc_IndexError,
                            "specified track does not exist");
            return NULL;
        }
        Py_DECREF(item);
    }

    Py_BEGIN_ALLOW_THREADS;
    err = sp_playlist_remove_tracks(self->_playlist, tracks, num_tracks);
    Py_END_ALLOW_THREADS;

    return handle_error(err);
}

static void
pl_callbacks_table_add(Playlist * pl, playlist_callback * cb)
{
    pl_cb_entry *curr, *entry = NULL;

    /* Look for an existing entry for this playlist */
    curr = playlist_callbacks_table;
    while (curr) {
        if (curr->playlist == pl->_playlist) {
            entry = curr;
            break;
        }
        curr = curr->next;
    }
    /* Update callbacks entry */
    if (entry) {
        cb->next = entry->callbacks;
        entry->callbacks = cb;
    }
    else {
        cb->next = NULL;
        entry = malloc(sizeof(pl_cb_entry));
        sp_playlist_add_ref(pl->_playlist);
        entry->playlist = pl->_playlist;
        entry->callbacks = cb;
        entry->next = playlist_callbacks_table;
        playlist_callbacks_table = entry;
    }
}

static playlist_callback *
pl_callbacks_table_remove(Playlist * pl,
                          PyObject *callback, PyObject *userdata)
{
    pl_cb_entry *e_prev = NULL, *e_curr, *entry = NULL;
    playlist_callback *c_prev = NULL, *c_curr;
    playlist_callback *result = NULL;
    PyObject *code1, *code2;

    /* Look for an existing entry for this playlist */
    e_curr = playlist_callbacks_table;
    while (e_curr) {
        if (e_curr->playlist == pl->_playlist) {
            entry = e_curr;
            break;
        }
        e_prev = e_curr;
        e_curr = e_curr->next;
    }
    /* Update callbacks entry */
    if (!entry) {
        return NULL;
    }
    else {
        c_curr = entry->callbacks;
        while (c_curr) {
            /* Note: a sole Python function can be represented by several
             * Python Function objects. However, to each function corresponds
             * an unique Code object.
             */
            PyObject *tmp1 = as_function(c_curr->trampoline->callback);
            PyObject *tmp2 = as_function(callback);
            code1 = PyFunction_GetCode(tmp1);
            code2 = PyFunction_GetCode(tmp2);
            if (code1 == code2 && c_curr->trampoline->userdata == userdata) {
                result = c_curr;
                if (c_prev) {
                    c_prev->next = c_curr->next;
                }
                else {
                    entry->callbacks = c_curr->next;
                };
                break;
            }
            c_prev = c_curr;
            c_curr = c_curr->next;
        }
    }
    if (!result)
        return NULL;
    /* Cleanup */
    if (!entry->callbacks) {
        if (e_prev) {
            e_prev->next = entry->next;
        }
        else {
            playlist_callbacks_table = entry->next;
        }
        sp_playlist_release(entry->playlist);
        free(entry);
    }
    return result;
}

static PyObject *
Playlist_add_callback(Playlist * self, PyObject *args,
                      sp_playlist_callbacks * pl_callbacks)
{
    PyObject *callback, *userdata = NULL;
    Callback *tramp;
    playlist_callback *to_add;

    if (!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;
    if (!userdata)
        userdata = Py_None;
    if (!(PyFunction_Check(callback) || PyMethod_Check(callback))) {
        PyErr_SetString(PyExc_TypeError,
                    "callback argument must be of function or method type");
        return NULL;
    }
    tramp = create_trampoline(callback, Py_None, userdata);
    to_add = malloc(sizeof(playlist_callback));
    to_add->callback = pl_callbacks;
    to_add->trampoline = tramp;
    pl_callbacks_table_add(self, to_add);
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-playlist- adding callback (%p,%p) py(%p,%p)\n",
            pl_callbacks, tramp, tramp->callback,
            tramp->userdata);
#endif
    sp_playlist_add_callbacks(self->_playlist, pl_callbacks, tramp);
    Py_RETURN_NONE;
}

void
playlist_tracks_added_callback(sp_playlist * playlist,
                               sp_track * const *tracks, int num_tracks,
                               int position, void *userdata)
{
    Callback *tramp = (Callback *) userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;
    PyObject *res;

    gstate = PyGILState_Ensure();
    for (i = 0; i < num_tracks; i++) {
        PyObject *track = Track_FromSpotify(tracks[i]);

        PyList_SetItem(py_tracks, i, track);
    }
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p,
                                       py_tracks,
                                       Py_BuildValue("i", position),
                                       tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_tracks_added_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->tracks_added = &playlist_tracks_added_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_tracks_removed_callback(sp_playlist * playlist, const int *tracks,
                                 int num_tracks, void *userdata)
{
    Callback *tramp = (Callback *) userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;
    PyObject *res;

    for (i = 0; i < num_tracks; i++) {
        PyList_SetItem(py_tracks, i, Py_BuildValue("i", tracks[i]));
    }
    gstate = PyGILState_Ensure();
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, py_tracks, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_tracks_removed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->tracks_removed = &playlist_tracks_removed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_tracks_moved_callback(sp_playlist * playlist, const int *tracks,
                               int num_tracks, int new_position,
                               void *userdata)
{
    Callback *tramp = (Callback *) userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;
    PyObject *res;

    for (i = 0; i < num_tracks; i++) {
        PyList_SetItem(py_tracks, i, Py_BuildValue("i", tracks[i]));
    }
    gstate = PyGILState_Ensure();
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p,
                                       py_tracks,
                                       Py_BuildValue("i", new_position),
                                       tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_tracks_moved_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->tracks_moved = &playlist_tracks_moved_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_renamed_callback(sp_playlist * playlist, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_renamed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->playlist_renamed = &playlist_renamed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_state_changed_callback(sp_playlist * playlist, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_state_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->playlist_state_changed = &playlist_state_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_update_in_progress_callback(sp_playlist * playlist,
                                     bool done, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res, *pdone;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    pdone = PyBool_FromLong(done);
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, pdone, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    Py_DECREF(pdone);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_update_in_progress_callback(Playlist * self,
                                                  PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->playlist_update_in_progress =
        &playlist_update_in_progress_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_metadata_updated_callback(sp_playlist * playlist, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_metadata_updated_callback(Playlist * self,
                                                PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->playlist_metadata_updated =
        &playlist_metadata_updated_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_track_created_changed_callback(sp_playlist * playlist,
                                        int position, sp_user * user,
                                        int when, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res, *ppos, *puser, *pwhen;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    ppos = PyInt_FromLong(position);
    puser = User_FromSpotify(user);
    pwhen = PyInt_FromLong(when);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p,
                                       ppos,
                                       puser, pwhen, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    Py_DECREF(ppos);
    Py_DECREF(puser);
    Py_DECREF(pwhen);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_track_created_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->track_created_changed =
        &playlist_track_created_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_track_message_changed_callback(sp_playlist * playlist,
                                        int position, const char *message,
                                        void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res, *ppos, *pmess;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    ppos = PyInt_FromLong(position);
    pmess = PyUnicode_FromString(message);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, ppos, pmess, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    Py_DECREF(ppos);
    Py_DECREF(pmess);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_track_message_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->track_message_changed =
        &playlist_track_message_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_track_seen_changed_callback(sp_playlist * playlist,
                                     int position, bool seen, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res, *ppos, *pseen;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    ppos = PyInt_FromLong(position);
    pseen = PyBool_FromLong(seen);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, ppos, pseen, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    Py_DECREF(ppos);
    Py_DECREF(pseen);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_track_seen_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->track_seen_changed = &playlist_track_seen_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_description_changed_callback(sp_playlist * playlist,
                                      const char *description, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res, *pdesc;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    pdesc = PyUnicode_FromString(description);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, pdesc, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    Py_DECREF(pdesc);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_description_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->description_changed =
        &playlist_description_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_subscribers_changed_callback(sp_playlist * playlist, void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_subscribers_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->subscribers_changed =
        &playlist_subscribers_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void
playlist_image_changed_callback(sp_playlist * playlist, const byte * image,
                                void *userdata)
{
    PyGILState_STATE gstate;
    Callback *tramp;
    PyObject *res, *pimage;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    PyObject *p = Playlist_FromSpotify(playlist);

    if (image) {
        pimage = PyBytes_FromStringAndSize((const char *)image, 20);        //TODO: return Image
    }
    else {
        Py_INCREF(Py_None);
        pimage = Py_None;
    }
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       p, pimage, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_XDECREF(res);
    Py_DECREF(p);
    Py_DECREF(pimage);
    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_image_changed_callback(Playlist * self, PyObject *args)
{
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->image_changed = &playlist_image_changed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

static PyObject *
Playlist_remove_callback(Playlist * self, PyObject *args)
{
    PyObject *callback, *userdata = NULL;
    playlist_callback *pl_callback;

    if (!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;
    if (!userdata) {
        userdata = Py_None;
    }
    if (!(callback = as_function(callback)))
        return NULL;
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-playlist- looking for callback py(%p,%p)\n",
            callback, userdata);
#endif
    pl_callback = pl_callbacks_table_remove(self, callback, userdata);
    if (!pl_callback) {
        PyErr_SetString(SpotifyError, "This callback was not added");
        return NULL;
    }
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-playlist- removing callback (%p,%p)\n",
            pl_callback->callback, pl_callback->trampoline);
#endif
    sp_playlist_remove_callbacks(self->_playlist, pl_callback->callback,
                                 pl_callback->trampoline);
    delete_trampoline(pl_callback->trampoline);
    free(pl_callback->callback);
    free(pl_callback);
    Py_RETURN_NONE;
}

static PyObject *
Playlist_track_create_time(Playlist * self, PyObject *args)
{
	int num_track;
	if (!PyArg_ParseTuple(args, "i", &num_track))
        return NULL;

	int when = sp_playlist_track_create_time(self->_playlist, num_track);
	return Py_BuildValue("i", when);
}

static PyObject *
Playlist_name(Playlist * self)
{
    const char *name = sp_playlist_name(self->_playlist);

    return PyUnicode_FromString(name);
}

static PyObject *
Playlist_rename(Playlist * self, PyObject *args)
{
    char *name = NULL;
    int len;
    sp_error error;

    if (!PyArg_ParseTuple(args, "es#", ENCODING, &name, &len))
        return NULL;
    if (len > 255) {
        PyErr_SetString(PyExc_ValueError, "Name too long (255ch max).");
        PyMem_Free(name);
        return NULL;
    }
    error = sp_playlist_rename(self->_playlist, (const char *) name);
    if (error) {
        PyErr_SetString(SpotifyError, sp_error_message(error));
        PyMem_Free(name);
        return NULL;
    }
    PyMem_Free(name);
    Py_RETURN_NONE;
}

static PyObject *
Playlist_owner(Playlist * self)
{
    return User_FromSpotify(sp_playlist_owner(self->_playlist));
}

static PyObject *
Playlist_is_collaborative(Playlist * self)
{
    return Py_BuildValue("i", sp_playlist_is_collaborative(self->_playlist));
}

static PyObject *
Playlist_num_subscribers(Playlist *self)
{
    return Py_BuildValue("i", sp_playlist_num_subscribers(self->_playlist));
}

static PyObject *
Playlist_subscribers(Playlist *self)
{
    sp_subscribers *subscribers;
    PyObject *list;
    unsigned int i;

    subscribers = sp_playlist_subscribers(self->_playlist);
    list = PyList_New(subscribers->count);
    for (i = 0; i < subscribers->count; i++) {
        PyList_SET_ITEM(list, i, PyUnicode_FromString(
                                        subscribers->subscribers[i]));
    }
    sp_playlist_subscribers_free(subscribers);
    return list;
}

static PyObject *
Playlist_update_subscribers(Playlist *self)
{
    if (!g_session) {
        PyErr_SetString(SpotifyError, "Not logged in.");
        return NULL;
    }
    sp_playlist_update_subscribers(g_session, self->_playlist);
    Py_RETURN_NONE;
}

static PyObject *
Playlist_add_tracks(Playlist *self, PyObject *args)
{
    int position, num_tracks;
    PyObject *tracks;
    int i;
    sp_error err;

    if (!sp_playlist_is_loaded(self->_playlist)) {
        PyErr_SetString(SpotifyError, "Playlist not loaded");
        return NULL;
    }
    if (!PyArg_ParseTuple(args, "iO!", &position, &PyList_Type, &tracks))
        return NULL;
    num_tracks = PyList_GET_SIZE(tracks);
    if (num_tracks <= 0)
        Py_RETURN_NONE;

    sp_track *ts[num_tracks];
    for (i = 0; i < num_tracks; i++) {
        PyObject *t = PyList_GetItem(tracks, i);
        if (t->ob_type != &TrackType) {
            PyErr_SetString(PyExc_TypeError,
                    "Expected a list of spotify.Track objects");
            return NULL;
        }
        ts[i] = ((Track *)t)->_track;
    }
    err = sp_playlist_add_tracks(self->_playlist, (sp_track *const *)ts,
                                 num_tracks, position, g_session);
    switch(err) {
        case SP_ERROR_OK:
            break;
        case SP_ERROR_INVALID_INDATA:
            PyErr_SetString(PyExc_IndexError,
                            "Cannot add tracks at this position");
            return NULL;
        default:
            PyErr_SetString(SpotifyError, sp_error_message(err));
            return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject *
Playlist_type(Playlist *self)
{
    return PyBytes_FromString("playlist");
}

/////////////// SEQUENCE PROTOCOL

Py_ssize_t
Playlist_sq_length(PyObject *o)
{
    Playlist *self = (Playlist *) o;

    return sp_playlist_num_tracks(self->_playlist);
}

PyObject *
Playlist_sq_item(PyObject *o, Py_ssize_t index)
{
    Playlist *self = (Playlist *) o;

    if (index >= sp_playlist_num_tracks(self->_playlist)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    sp_track *tr = sp_playlist_track(self->_playlist, (int)index);
    PyObject *track = Track_FromSpotify(tr);

    return track;
}

/////////////// ADDITIONAL METHODS

static PyObject *
Playlist_str(PyObject *o)
{
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyMethodDef Playlist_methods[] = {
    {"is_loaded",
     (PyCFunction)Playlist_is_loaded,
     METH_NOARGS,
     "True if this playlist has been loaded by the client"},
    {"is_collaborative",
     (PyCFunction)Playlist_is_collaborative,
     METH_NOARGS,
     "Return collaborative status for a playlist. A playlist in collaborative state can be modifed by all users, not only the user owning the list"},
    {"add_tracks",
     (PyCFunction)Playlist_add_tracks,
     METH_VARARGS,
     ""},
    {"remove_tracks",
     (PyCFunction)Playlist_remove_tracks,
     METH_VARARGS,
     "Remove tracks from a playlist"},
    {"add_tracks_added_callback",
     (PyCFunction)Playlist_add_tracks_added_callback,
     METH_VARARGS,
     ""},
    {"add_tracks_removed_callback",
     (PyCFunction)Playlist_add_tracks_removed_callback,
     METH_VARARGS,
     ""},
    {"add_tracks_moved_callback",
     (PyCFunction)Playlist_add_tracks_moved_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_renamed_callback",
     (PyCFunction)Playlist_add_playlist_renamed_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_state_changed_callback",
     (PyCFunction)Playlist_add_playlist_state_changed_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_update_in_progress_callback",
     (PyCFunction)Playlist_add_playlist_update_in_progress_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_metadata_updated_callback",
     (PyCFunction)Playlist_add_playlist_metadata_updated_callback,
     METH_VARARGS,
     ""},
    {"add_track_created_changed_callback",
     (PyCFunction)Playlist_add_track_created_changed_callback,
     METH_VARARGS,
     ""},
    {"add_track_message_changed_callback",
     (PyCFunction)Playlist_add_track_message_changed_callback,
     METH_VARARGS,
     ""},
    {"add_track_seen_changed_callback",
     (PyCFunction)Playlist_add_track_seen_changed_callback,
     METH_VARARGS,
     ""},
    {"add_description_changed_callback",
     (PyCFunction)Playlist_add_description_changed_callback,
     METH_VARARGS,
     ""},
    {"add_subscribers_changed_callback",
     (PyCFunction)Playlist_add_subscribers_changed_callback,
     METH_VARARGS,
     ""},
    {"add_image_changed_callback",
     (PyCFunction)Playlist_add_image_changed_callback,
     METH_VARARGS,
     ""},
    {"remove_callback",
     (PyCFunction)Playlist_remove_callback,
     METH_VARARGS,
     ""},
 	{"track_create_time",
     (PyCFunction)Playlist_track_create_time,
     METH_VARARGS,
     "Return when the given index was added to the playlist"},
    {"name",
     (PyCFunction)Playlist_name,
     METH_NOARGS,
     "Returns the name of the playlist"},
    {"rename",
     (PyCFunction)Playlist_rename,
     METH_VARARGS,
     "Renames the playlist."},
    {"owner",
     (PyCFunction)Playlist_owner,
     METH_NOARGS,
     "Returns the owner of the playlist"},
    {"num_subscribers",
     (PyCFunction)Playlist_num_subscribers,
     METH_NOARGS,
     "Returns the number of subscribers this playlist currently has"},
    {"subscribers",
     (PyCFunction)Playlist_subscribers,
     METH_NOARGS,
     "Returns a list of subscribers (canonical_name) to this playlist"},
    {"update_subscribers",
     (PyCFunction)Playlist_update_subscribers,
     METH_NOARGS,
     "Update the subscribers information for this playlist"},
    {"type",
     (PyCFunction)Playlist_type,
     METH_NOARGS,
     ""},
    {NULL}
};

static PySequenceMethods Playlist_as_sequence = {
    Playlist_sq_length, // sq_length
    0,                  // sq_concat
    0,                  // sq_repeat
    Playlist_sq_item,   // sq_item
    0,                  //Playlist_sq_ass_item,  // sq_ass_item
    0,                  // sq_contains
    0,                  // sq_inplace_concat
    0,                  // sq_inplace_repeat
};

PyTypeObject PlaylistType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.Playlist", /*tp_name */
    sizeof(Playlist),   /*tp_basicsize */
    0,                  /*tp_itemsize */
    (destructor) Playlist_dealloc,      /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    &Playlist_as_sequence,      /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    Playlist_str,       /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "Playlist objects", /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    Playlist_methods,   /* tp_methods */
    Playlist_members,   /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    Playlist_new,       /* tp_new */
};

void
playlist_init(PyObject *m)
{
    Py_INCREF(&PlaylistType);
    PyModule_AddObject(m, "Playlist", (PyObject *)&PlaylistType);
}
