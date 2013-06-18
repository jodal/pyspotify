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

/* Mallocs and memsets a new sp_playlist_callbacks structure. */
static sp_playlist_callbacks *
create_and_initialize_callbacks(void) {
    /* TODO: switch to PyMem_Malloc and audit for coresponding free */
    sp_playlist_callbacks *callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(callbacks, 0, sizeof(sp_playlist_callbacks));
    return callbacks;
}

/* TODO: cleanup table add and remove */
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
        /* TODO: switch to PyMem_Malloc and audit for coresponding free */
        entry = malloc(sizeof(pl_cb_entry));
        sp_playlist_add_ref(pl->_playlist);
        entry->playlist = pl->_playlist;
        entry->callbacks = cb;
        entry->next = playlist_callbacks_table;
        playlist_callbacks_table = entry;
    }
}

static playlist_callback *
pl_callbacks_table_remove(Playlist *pl,
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
Playlist_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Playlist_SP_PLAYLIST(self) = NULL;
    return self;
}

PyObject *
Playlist_FromSpotify(sp_playlist *playlist)
{
    PyObject *self = PlaylistType.tp_alloc(&PlaylistType, 0);
    Playlist_SP_PLAYLIST(self) = playlist;
    sp_playlist_add_ref(playlist);
    /* TODO: move to helper for setting playlist defaults */
    sp_playlist_set_autolink_tracks(playlist, 1);
    return self;
}

static void
Playlist_dealloc(PyObject *self)
{
    if (Playlist_SP_PLAYLIST(self) != NULL)
        sp_playlist_release(Playlist_SP_PLAYLIST(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Playlist_is_loaded(PyObject *self)
{
    return PyBool_FromLong(sp_playlist_is_loaded(Playlist_SP_PLAYLIST(self)));
}

static PyObject *
Playlist_remove_tracks(PyObject *self, PyObject *args)
{
    PyObject *item, *py_indicies;
    sp_error error;

    int *indices;
    int i, num_tracks, playlist_length;

    if (!PyArg_ParseTuple(args, "O", &py_indicies))
        return NULL;
    if (!PySequence_Check(py_indicies)) {
        PyErr_SetString(PyExc_TypeError, "expected sequence");
        return NULL;
    }

    playlist_length = sp_playlist_num_tracks(Playlist_SP_PLAYLIST(self));

    num_tracks = (int)PySequence_Size(py_indicies);
    /* TODO: could we use int *indices[num_tracks]; instead? */
    indices = PyMem_New(int, num_tracks);

    for (i = 0; i < num_tracks; i++) {
        item = PySequence_GetItem(py_indicies, i);
        indices[i] = (int)PyInt_AsLong(item);
        Py_DECREF(item);

        if (indices[i] == -1 && PyErr_Occurred() != NULL) {
            PyMem_Free(indices);
            return NULL;
        }

        if (indices[i] < 0 || indices[i] > playlist_length) {
            PyErr_SetString(PyExc_IndexError, "specified track does not exist");
            PyMem_Free(indices);
            return NULL;
        }
    }

    Py_BEGIN_ALLOW_THREADS;
    error = sp_playlist_remove_tracks(
        Playlist_SP_PLAYLIST(self), indices, num_tracks);
    Py_END_ALLOW_THREADS;

    PyMem_Free(indices);
    return none_or_raise_error(error);
}

/* TODO: cleanup add and remove callback */
static PyObject *
Playlist_add_callback(PyObject *self, PyObject *args, sp_playlist_callbacks *playlist_callbacks)
{
    PyObject *callback, *userdata = NULL;
    Callback *trampoline;
    playlist_callback *entry;

    if (!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;

    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError,
                        "callback argument must be of function or method type");
        return NULL;
    }

    trampoline = create_trampoline(callback, userdata);

    /* TODO: switch to PyMem_Malloc and audit for coresponding free */
    /* TODO: extract to helper */
    entry = malloc(sizeof(playlist_callbacks));
    entry->callback = playlist_callbacks;
    entry->trampoline = trampoline;
    pl_callbacks_table_add((Playlist *)self, entry);

    debug_printf("adding callback (%p,%p) py(%p,%p)",
                 playlist_callbacks, trampoline, trampoline->callback,
                 trampoline->userdata);

    sp_playlist_add_callbacks(
        Playlist_SP_PLAYLIST(self), playlist_callbacks, (void *)trampoline);
    Py_RETURN_NONE;
}

static PyObject *
Playlist_remove_callback(PyObject *self, PyObject *args)
{
    PyObject *callback, *userdata = NULL;
    playlist_callback *entry;

    if (!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;

    if (userdata == NULL) {
        /* Missing incref for this use of Py_None should be fine as we are
         * simply borrowing it and not giving it to anyone that changes the
         * userdata count. */
        userdata = Py_None;
    }

    if (!(callback = as_function(callback)))
        return NULL;

    debug_printf("looking for callback py(%p,%p)", callback, userdata);
    entry = pl_callbacks_table_remove((Playlist *)self, callback, userdata);

    if (entry == NULL) {
        PyErr_SetString(SpotifyError, "This callback was not added");
        return NULL;
    }

    debug_printf("removing callback (%p,%p)", entry->callback,
                 entry->trampoline);

    sp_playlist_remove_callbacks(Playlist_SP_PLAYLIST(self), entry->callback,
                                 entry->trampoline);

    delete_trampoline(entry->trampoline);
    free(entry->callback);
    free(entry);

    Py_RETURN_NONE;
}

void
playlist_tracks_added_callback(sp_playlist *playlist, sp_track *const *tracks,
                               int num_tracks, int position, void *data)
{
    Callback *trampoline = (Callback *)data;

    int i;
    PyObject *result, *self, *py_tracks;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    py_tracks = PyList_New(num_tracks);

    /* TODO: Create Tracks_FromSpotify(tracks, num), Albums...? */
    for (i = 0; i < num_tracks; i++) {
        PyObject *track = Track_FromSpotify(tracks[i]);
        PyList_SET_ITEM(py_tracks, i, track);
    }

    result = PyObject_CallFunction(trampoline->callback, "OOiO", self,
                                   py_tracks, position, trampoline->userdata);
    Py_XDECREF(self);
    Py_XDECREF(py_tracks);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_tracks_added_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->tracks_added = &playlist_tracks_added_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_tracks_removed_callback(
    sp_playlist *playlist, const int *tracks, int num_tracks, void *data)
{
    Callback *trampoline = (Callback *)data;

    int i;
    PyObject *result, *self, *removed;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    removed = PyList_New(num_tracks);

    for (i = 0; i < num_tracks; i++) {
        PyList_SET_ITEM(removed, i, Py_BuildValue("i", tracks[i]));
    }

    result = PyObject_CallFunction(trampoline->callback, "OOO", self,
                                   removed, trampoline->userdata);
    Py_XDECREF(self);
    Py_XDECREF(removed);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_tracks_removed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->tracks_removed = &playlist_tracks_removed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_tracks_moved_callback(
    sp_playlist *playlist, const int *tracks, int num_tracks, int new_position,
    void *data)
{
    Callback *trampoline = (Callback *)data;

    int i;
    PyObject *result, *self, *moved;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    moved = PyList_New(num_tracks);

    for (i = 0; i < num_tracks; i++) {
        PyList_SET_ITEM(moved, i, Py_BuildValue("i", tracks[i]));
    }

    result = PyObject_CallFunction(trampoline->callback, "OOiO", self,
                                   moved, new_position, trampoline->userdata);
    Py_XDECREF(self);
    Py_XDECREF(moved);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_tracks_moved_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->tracks_moved = &playlist_tracks_moved_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_renamed_callback(sp_playlist *playlist, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    result = PyObject_CallFunction(trampoline->callback, "OO", self,
                                   trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_renamed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_renamed = &playlist_renamed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_state_changed_callback(sp_playlist *playlist, void *data)
{
    /* TODO: indenditical with playlist_renamed_callback... */
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    result = PyObject_CallFunction(trampoline->callback, "OO", self,
                                   trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_state_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_state_changed = &playlist_state_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_update_in_progress_callback(sp_playlist *playlist, bool done, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);

    /* TODO: bool instead of int for done? */
    result = PyObject_CallFunction(trampoline->callback, "OiO", self,
                                   done, trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_update_in_progress_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_update_in_progress = &playlist_update_in_progress_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_metadata_updated_callback(sp_playlist * playlist, void *data)
{
    /* TODO: indenditical with playlist_renamed_callback... */
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    result = PyObject_CallFunction(trampoline->callback, "OO", self,
                                   trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_playlist_metadata_updated_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_metadata_updated = &playlist_metadata_updated_callback;
    return Playlist_add_callback((PyObject *)self, args, callbacks);
}

void
playlist_track_created_changed_callback(
    sp_playlist *playlist, int position, sp_user *user, int when, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self, *py_user;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    py_user = User_FromSpotify(user);

    result = PyObject_CallFunction(trampoline->callback, "OiOiO", self,
                                   position, py_user, when, trampoline->userdata);
    Py_XDECREF(self);
    Py_XDECREF(py_user);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_track_created_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->track_created_changed = &playlist_track_created_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_track_message_changed_callback(
    sp_playlist *playlist, int position, const char *message, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self, *py_message;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    py_message = PyUnicode_FromString(message);
    result = PyObject_CallFunction(trampoline->callback, "OiOO", self,
                                   position, py_message, trampoline->userdata);
    Py_XDECREF(self);
    Py_XDECREF(py_message);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_track_message_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->track_message_changed = &playlist_track_message_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_track_seen_changed_callback(
    sp_playlist *playlist, int position, bool seen, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);

    /* TODO: bool instead of int for seen? */
    result = PyObject_CallFunction(trampoline->callback, "OiiO", self,
                                   position, seen, trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_track_seen_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->track_seen_changed = &playlist_track_seen_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_description_changed_callback(
    sp_playlist *playlist, const char *description, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self, *py_description;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    py_description = PyUnicode_FromString(description);
    result = PyObject_CallFunction(trampoline->callback, "OOO", self,
                                   py_description, trampoline->userdata);
    Py_XDECREF(self);
    Py_XDECREF(py_description);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_description_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->description_changed = &playlist_description_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_subscribers_changed_callback(sp_playlist *playlist, void *data)
{
    /* TODO: indenditical with playlist_renamed_callback... */
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);
    result = PyObject_CallFunction(trampoline->callback, "OO", self,
                                   trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_subscribers_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->subscribers_changed = &playlist_subscribers_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

void
playlist_image_changed_callback(
    sp_playlist * playlist, const byte *image, void *data)
{
    Callback *trampoline = (Callback *)data;

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = Playlist_FromSpotify(playlist);

    /* TODO: go with a Image_FromSpotify or an image from id instead? */
    result = PyObject_CallFunction(trampoline->callback, "Os#O", self,
                                   image, 20, trampoline->userdata);
    Py_XDECREF(self);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
Playlist_add_image_changed_callback(PyObject *self, PyObject *args)
{
    sp_playlist_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->image_changed = &playlist_image_changed_callback;
    return Playlist_add_callback(self, args, callbacks);
}

static PyObject *
Playlist_track_create_time(PyObject *self, PyObject *args)
{
	int index;
	if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;

	return Py_BuildValue("i", sp_playlist_track_create_time(
        Playlist_SP_PLAYLIST(self), index));
}

static PyObject *
Playlist_name(PyObject *self)
{
    const char *name = sp_playlist_name(Playlist_SP_PLAYLIST(self));
    return PyUnicode_FromString(name);
}

static PyObject *
Playlist_rename(PyObject *self, PyObject *args)
{
    char *name = NULL;
    int len;
    sp_error error;

    if (!PyArg_ParseTuple(args, "es#", ENCODING, &name, &len))
        return NULL;

    if (len > 255) {
        PyErr_SetString(PyExc_ValueError, "Name too long (255ch max).");
        return NULL;
    }

    error = sp_playlist_rename(Playlist_SP_PLAYLIST(self), (const char *)name);
    return none_or_raise_error(error);
}

static PyObject *
Playlist_owner(PyObject *self)
{
    return User_FromSpotify(sp_playlist_owner(Playlist_SP_PLAYLIST(self)));
}

static PyObject *
Playlist_is_collaborative(PyObject *self)
{
    bool collaborative = sp_playlist_is_collaborative(Playlist_SP_PLAYLIST(self));
    return PyBool_FromLong(collaborative);
}

static PyObject *
Playlist_num_subscribers(Playlist *self)
{
    int subscribers = sp_playlist_num_subscribers(Playlist_SP_PLAYLIST(self));
    return Py_BuildValue("i", subscribers);
}

static PyObject *
Playlist_subscribers(PyObject *self)
{
    unsigned int i;

    sp_subscribers *subscribers = sp_playlist_subscribers(
        Playlist_SP_PLAYLIST(self));
    PyObject *list = PyList_New(subscribers->count);

    for (i = 0; i < subscribers->count; i++)
        PyList_SET_ITEM(
            list, i, PyUnicode_FromString(subscribers->subscribers[i]));

    sp_playlist_subscribers_free(subscribers);
    return list;
}

static PyObject *
Playlist_update_subscribers(PyObject *self)
{
    if (!g_session) {
        PyErr_SetString(SpotifyError, "Not logged in.");
        return NULL;
    }
    sp_playlist_update_subscribers(g_session, Playlist_SP_PLAYLIST(self));
    Py_RETURN_NONE;
}

static PyObject *
Playlist_add_tracks(PyObject *self, PyObject *args)
{
    int position, num_tracks;
    PyObject *py_tracks;
    int i;

    sp_error error;
    sp_playlist *playlist = Playlist_SP_PLAYLIST(self);

    if (!sp_playlist_is_loaded(playlist)) {
        PyErr_SetString(SpotifyError, "Playlist not loaded");
        return NULL;
    }

    /* TODO: use py check sequence instead? */
    if (!PyArg_ParseTuple(args, "iO!", &position, &PyList_Type, &py_tracks))
        return NULL;

    num_tracks = (int)PyList_Size(py_tracks);
    if (num_tracks <= 0)
        Py_RETURN_NONE;

    sp_track *tracks[num_tracks];
    for (i = 0; i < num_tracks; i++) {
        PyObject *track = PyList_GetItem(py_tracks, i);
        if (Py_TYPE(track) != &TrackType) {
            PyErr_SetString(PyExc_TypeError,
                            "Expected a list of spotify.Track objects");
            return NULL;
        }
        tracks[i] = Track_SP_TRACK(track);
    }
    error = sp_playlist_add_tracks(
        playlist, (sp_track *const *)tracks, num_tracks, position, g_session);

    if (error == SP_ERROR_INVALID_INDATA) {
        PyErr_SetString(PyExc_IndexError,
                        "Cannot add tracks at this position");
        return NULL;
    }
    return none_or_raise_error(error);
}

static PyObject *
Playlist_type(PyObject *self)
{
    return PyBytes_FromString("playlist");
}

static PyObject *
Playlist_str(PyObject * self)
{
    return Playlist_name(self);
}

/* sequence protocol: */
Py_ssize_t
Playlist_sq_length(PyObject *self)
{
    return sp_playlist_num_tracks(Playlist_SP_PLAYLIST(self));
}

PyObject *
Playlist_sq_item(PyObject *self, Py_ssize_t index)
{
    if (index >= sp_playlist_num_tracks(Playlist_SP_PLAYLIST(self))) {
        PyErr_SetNone(PyExc_IndexError);
        return NULL;
    }
    sp_track *track = sp_playlist_track(
        Playlist_SP_PLAYLIST(self), (int)index);
    return Track_FromSpotify(track);
}

static PyMethodDef Playlist_methods[] = {
    {"is_loaded",
     (PyCFunction)Playlist_is_loaded, METH_NOARGS,
     "True if this playlist has been loaded by the client"
    },
    {"is_collaborative",
     (PyCFunction)Playlist_is_collaborative, METH_NOARGS,
     "Return collaborative status for a playlist. A playlist in " \
     "collaborative state can be modifed by all users, not only the user " \
     "owning the list."
    },
    {"add_tracks",
     (PyCFunction)Playlist_add_tracks, METH_VARARGS,
     ""
    },
    {"remove_tracks",
     (PyCFunction)Playlist_remove_tracks, METH_VARARGS,
     "Remove tracks from a playlist"
    },
    {"add_tracks_added_callback",
     (PyCFunction)Playlist_add_tracks_added_callback, METH_VARARGS,
     ""
    },
    {"add_tracks_removed_callback",
     (PyCFunction)Playlist_add_tracks_removed_callback, METH_VARARGS,
     ""
    },
    {"add_tracks_moved_callback",
     (PyCFunction)Playlist_add_tracks_moved_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_renamed_callback",
     (PyCFunction)Playlist_add_playlist_renamed_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_state_changed_callback",
     (PyCFunction)Playlist_add_playlist_state_changed_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_update_in_progress_callback",
     (PyCFunction)Playlist_add_playlist_update_in_progress_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_metadata_updated_callback",
     (PyCFunction)Playlist_add_playlist_metadata_updated_callback, METH_VARARGS,
     ""
    },
    {"add_track_created_changed_callback",
     (PyCFunction)Playlist_add_track_created_changed_callback, METH_VARARGS,
     ""
    },
    {"add_track_message_changed_callback",
     (PyCFunction)Playlist_add_track_message_changed_callback, METH_VARARGS,
     ""
    },
    {"add_track_seen_changed_callback",
     (PyCFunction)Playlist_add_track_seen_changed_callback, METH_VARARGS,
     ""
    },
    {"add_description_changed_callback",
     (PyCFunction)Playlist_add_description_changed_callback, METH_VARARGS,
     ""
    },
    {"add_subscribers_changed_callback",
     (PyCFunction)Playlist_add_subscribers_changed_callback, METH_VARARGS,
     ""
    },
    {"add_image_changed_callback",
     (PyCFunction)Playlist_add_image_changed_callback, METH_VARARGS,
     ""
    },
    {"remove_callback",
     (PyCFunction)Playlist_remove_callback, METH_VARARGS,
     ""
    },
 	{"track_create_time",
     (PyCFunction)Playlist_track_create_time, METH_VARARGS,
     "Return when the given index was added to the playlist"
    },
    {"name",
     (PyCFunction)Playlist_name, METH_NOARGS,
     "Returns the name of the playlist"
    },
    {"rename",
     (PyCFunction)Playlist_rename, METH_VARARGS,
     "Renames the playlist."
    },
    {"owner",
     (PyCFunction)Playlist_owner, METH_NOARGS,
     "Returns the owner of the playlist"
    },
    {"num_subscribers",
     (PyCFunction)Playlist_num_subscribers, METH_NOARGS,
     "Returns the number of subscribers this playlist currently has"
    },
    {"subscribers",
     (PyCFunction)Playlist_subscribers, METH_NOARGS,
     "Returns a list of subscribers (canonical_name) to this playlist"
    },
    {"update_subscribers",
     (PyCFunction)Playlist_update_subscribers, METH_NOARGS,
     "Update the subscribers information for this playlist"
    },
    {"type",
     (PyCFunction)Playlist_type, METH_NOARGS,
     ""
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Playlist_members[] = {
    {NULL} /* Sentinel */
};

static PySequenceMethods Playlist_as_sequence = {
    Playlist_sq_length, /*sq_length*/
    0,                  /*sq_concat*/
    0,                  /*sq_repeat*/
    Playlist_sq_item,   /*sq_item*/
    0,                  /*sq_ass_item*/
    0,                  /*sq_contains*/
    0,                  /*sq_inplace_concat*/
    0,                  /*sq_inplace_repeat*/
};

PyTypeObject PlaylistType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Playlist",                       /*tp_name*/
    sizeof(Playlist),                         /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) Playlist_dealloc,            /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    &Playlist_as_sequence,                    /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    Playlist_str,                             /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Playlist objects",                       /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Playlist_methods,                         /* tp_methods */
    Playlist_members,                         /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Playlist_new,                             /* tp_new */
};

void
playlist_init(PyObject *module)
{
    Py_INCREF(&PlaylistType);
    PyModule_AddObject(module, "Playlist", (PyObject *)&PlaylistType);
}
