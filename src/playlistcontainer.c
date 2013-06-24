#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include "pyspotify.h"
#include "playlistcontainer.h"
#include "playlist.h"
#include "playlistfolder.h"

/* This is the playlist container callbacks table.
 *
 * It is a linked list of entries keeping enough information into pyspotify
 * to be able to remove the callbacks after a while, especially when dealing
 * with a different python PlaylistContainer object than the one the callbacks
 * were added from. Each entry corresponds to a spotify playlist container on
 * which callbacks have been added. When all callbacks are removed from a
 * playlist container, the entry is free'd from memory.
 */
static plc_cb_entry *playlistcontainer_callbacks_table = NULL;

/* Mallocs and memsets a new sp_playlist_callbacks structure. */
static sp_playlistcontainer_callbacks *
create_and_initialize_callbacks(void) {
    /* TODO: switch to PyMem_Malloc and audit for coresponding free */
    sp_playlistcontainer_callbacks *callbacks = malloc(
        sizeof(sp_playlistcontainer_callbacks));
    memset(callbacks, 0, sizeof(sp_playlistcontainer_callbacks));
    return callbacks;
}

static PyObject *
PlaylistContainer_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    PlaylistContainer_SP_PLAYLISTCONTAINER(self) = NULL;
    return self;
}

PyObject *
PlaylistContainer_FromSpotify(sp_playlistcontainer *container, bool add_ref)
{
    PyObject *self = PlaylistContainerType.tp_alloc(&PlaylistContainerType, 0);
    PlaylistContainer_SP_PLAYLISTCONTAINER(self) = container;
    if (add_ref)
        sp_playlistcontainer_add_ref(container);
    return self;
}

static void
PlaylistContainer_dealloc(PyObject *self)
{
    if (PlaylistContainer_SP_PLAYLISTCONTAINER(self) != NULL)
        sp_playlistcontainer_release(PlaylistContainer_SP_PLAYLISTCONTAINER(self));
    self->ob_type->tp_free(self);
}

/* TODO: cleanup this code with respect to variables and formating */
static void
plc_callbacks_table_add(PlaylistContainer *plc,
                        playlistcontainer_callback * cb)
{
    plc_cb_entry *curr, *entry = NULL;

    /* Look for an existing entry for this playlist */
    curr = playlistcontainer_callbacks_table;
    while (curr) {
        if (curr->playlistcontainer == plc->_playlistcontainer) {
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
        entry = malloc(sizeof(plc_cb_entry));
        sp_playlistcontainer_add_ref(plc->_playlistcontainer);
        entry->playlistcontainer = plc->_playlistcontainer;
        entry->callbacks = cb;
        entry->next = playlistcontainer_callbacks_table;
        playlistcontainer_callbacks_table = entry;
    }
}

static PyObject *
PlaylistContainer_add_callback(PyObject *self, PyObject *args,
                               sp_playlistcontainer_callbacks *container_callbacks)
{
    PyObject *callback, *userdata = NULL;
    Callback *trampoline;
    playlistcontainer_callback *to_add;

    if (!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;

    /* TODO: none of our other callback add functions check this... */
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError,
                        "callback argument must be of function or method type");
        return NULL;
    }

    trampoline = create_trampoline(callback, userdata);

    /* TODO: switch to PyMem_Malloc and audit for coresponding free */
    /* TODO: extract to helper */
    to_add = malloc(sizeof(playlistcontainer_callback));
    to_add->callback = container_callbacks;
    to_add->trampoline = trampoline;
    plc_callbacks_table_add((PlaylistContainer *)self, to_add);

    debug_printf("adding callback (%p,%p) py(%p,%p)",
                 container_callbacks, trampoline, trampoline->callback,
                 trampoline->userdata);

    sp_playlistcontainer_add_callbacks(
            PlaylistContainer_SP_PLAYLISTCONTAINER(self), container_callbacks,
            (void *)trampoline);
    Py_RETURN_NONE;
}

void
playlistcontainer_loaded_callback(sp_playlistcontainer *container, void *data)
{
    Callback *trampoline = (Callback *)data;
    debug_printf("container loaded (%p, %p)", container, trampoline);

    PyObject *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = PlaylistContainer_FromSpotify(container, 1 /* add_ref */);
    result = PyObject_CallFunction(trampoline->callback, "NO", self,
                                   trampoline->userdata);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_loaded_callback(PyObject *self, PyObject *args)
{
    sp_playlistcontainer_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->container_loaded = &playlistcontainer_loaded_callback;
    return PlaylistContainer_add_callback(self, args, callbacks);
}

void
playlistcontainer_playlist_added_callback(
    sp_playlistcontainer *container, sp_playlist *playlist, int position, void *data)
{
    Callback *trampoline = (Callback *)data;
    if (trampoline == NULL)
        return;

    PyObject *py_playlist, *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = PlaylistContainer_FromSpotify(container, 1 /* add_ref */);
    py_playlist = Playlist_FromSpotify(playlist, 1 /* add_ref */);

    result = PyObject_CallFunction(trampoline->callback, "NNiO",
                                   self, py_playlist, position,
                                   trampoline->userdata);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_playlist_added_callback(PyObject *self, PyObject *args)
{
    sp_playlistcontainer_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_added = &playlistcontainer_playlist_added_callback;
    return PlaylistContainer_add_callback(self, args, callbacks);
}

void
playlistcontainer_playlist_moved_callback(
    sp_playlistcontainer * container, sp_playlist *playlist, int position,
    int new_position, void *data)
{
    Callback *trampoline = (Callback *)data;
    if (trampoline == NULL)
        return;

    PyObject *py_playlist, *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = PlaylistContainer_FromSpotify(container, 1 /* add_ref */);
    py_playlist = Playlist_FromSpotify(playlist, 1 /* add_ref */);

    result = PyObject_CallFunction(trampoline->callback, "NNiiO", self,
                                   py_playlist, position, new_position,
                                   trampoline->userdata);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_playlist_moved_callback(PyObject *self, PyObject *args)
{
    sp_playlistcontainer_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_moved = &playlistcontainer_playlist_moved_callback;
    return PlaylistContainer_add_callback(self, args, callbacks);
}

void
playlistcontainer_playlist_removed_callback(
    sp_playlistcontainer *container, sp_playlist *playlist, int position, void *data)
{
    /* TODO: this code is identical to playlist add... */
    Callback *trampoline = (Callback *)data;
    if (trampoline == NULL)
        return;

    PyObject *py_playlist, *result, *self;
    PyGILState_STATE gstate = PyGILState_Ensure();

    self = PlaylistContainer_FromSpotify(container, 1 /* add_ref */);
    py_playlist = Playlist_FromSpotify(playlist, 1 /* add_ref */);

    result = PyObject_CallFunction(trampoline->callback, "NNiO",
                                   self, py_playlist, position,
                                   trampoline->userdata);

    if (result != NULL)
        Py_DECREF(result);
    else
        PyErr_WriteUnraisable(trampoline->callback);

    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_playlist_removed_callback(PyObject *self, PyObject *args)
{
    sp_playlistcontainer_callbacks *callbacks = create_and_initialize_callbacks();
    callbacks->playlist_removed = &playlistcontainer_playlist_removed_callback;
    return PlaylistContainer_add_callback(self, args, callbacks);
}

static PyObject *
PlaylistContainer_str(PyObject *self)
{
    PyErr_SetNone(PyExc_NotImplementedError);
    return NULL;
}

static PyObject *
PlaylistContainer_remove_playlist(PyObject *self, PyObject *args)
{
    sp_error error;
    sp_playlistcontainer *container = PlaylistContainer_SP_PLAYLISTCONTAINER(self);

    int index;
    if (!sp_playlistcontainer_is_loaded(container)) {
        PyErr_SetString(SpotifyError, "PlaylistContainer not loaded");
        return NULL;
    }
    if (!PyArg_ParseTuple(args, "i", &index)){
        return NULL;
    }
    if (index >= sp_playlistcontainer_num_playlists(container)) {
        PyErr_SetNone(PyExc_IndexError);
        return NULL;
    }

    error = sp_playlistcontainer_remove_playlist(container, index);
    return Py_BuildValue("i", error);
}

static PyObject *
PlaylistContainer_add_new_playlist(PyObject *self, PyObject *args)
{
    sp_playlist *playlist;
    sp_playlistcontainer *container = PlaylistContainer_SP_PLAYLISTCONTAINER(self);

    char *name = NULL;
    int len;

    if (!sp_playlistcontainer_is_loaded(container)) {
        PyErr_SetString(SpotifyError, "PlaylistContainer not loaded");
        return NULL;
    }
    if (!PyArg_ParseTuple(args, "es#", ENCODING, &name, &len))
        return NULL;

    if (len > 255) {
        PyErr_SetString(PyExc_ValueError,
                        "Playlist name must be < 255 characters long");
        PyMem_Free(name);
        return NULL;
    }
    playlist = sp_playlistcontainer_add_new_playlist(container, name);
    PyMem_Free(name);

    return Playlist_FromSpotify(playlist, 0 /* add_ref */);
}

/* sequence protocol: */
Py_ssize_t
PlaylistContainer_sq_length(PyObject *self)
{
    return sp_playlistcontainer_num_playlists(
        PlaylistContainer_SP_PLAYLISTCONTAINER(self));
}

PyObject *
PlaylistContainer_sq_item(PyObject *self, Py_ssize_t index)
{
    sp_playlistcontainer *container = PlaylistContainer_SP_PLAYLISTCONTAINER(self);
    sp_playlist_type type;

    if (index >= sp_playlistcontainer_num_playlists(container)) {
        PyErr_SetNone(PyExc_IndexError);
        return NULL;
    }

    type = sp_playlistcontainer_playlist_type(container, (int)index);
    if (type == SP_PLAYLIST_TYPE_PLAYLIST)
        return Playlist_FromSpotify(
            sp_playlistcontainer_playlist(container, (int)index), 1 /* add_ref */);
    else
        return PlaylistFolder_FromSpotify(container, (int)index, type);
}

PyObject *
PlaylistContainer_sq_ass_item(PyObject *self, Py_ssize_t index, Py_ssize_t meh)
{
    /* TODO: why not just remove this from PlaylistContainer_as_sequence? */
    PyErr_SetNone(PyExc_NotImplementedError);
    return NULL;
}

PySequenceMethods PlaylistContainer_as_sequence = {
    PlaylistContainer_sq_length,   /*sq_length*/
    0,                             /*sq_concat*/
    0,                             /*sq_repeat*/
    PlaylistContainer_sq_item,     /*sq_item*/
    PlaylistContainer_sq_ass_item, /*sq_ass_item*/
    0,                             /*sq_contains*/
    0,                             /*sq_inplace_concat*/
    0,                             /*sq_inplace_repeat*/
};

static PyMethodDef PlaylistContainer_methods[] = {
    {"add_loaded_callback",
     (PyCFunction)PlaylistContainer_add_loaded_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_added_callback",
     (PyCFunction)PlaylistContainer_add_playlist_added_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_moved_callback",
     (PyCFunction)PlaylistContainer_add_playlist_moved_callback, METH_VARARGS,
     ""
    },
    {"add_playlist_removed_callback",
     (PyCFunction)PlaylistContainer_add_playlist_removed_callback, METH_VARARGS,
     ""},
    {"remove_playlist",
     (PyCFunction)PlaylistContainer_remove_playlist, METH_VARARGS,
     "Remove a playlist from the playlistcontainer"
    },
    {"add_new_playlist",
     (PyCFunction)PlaylistContainer_add_new_playlist, METH_VARARGS,
     "Add a new empty playlist to the playlist container."
    },
    {NULL} /* Sentinel */
};

static PyMemberDef PlaylistContainer_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject PlaylistContainerType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.PlaylistContainer",              /*tp_name*/
    sizeof(PlaylistContainer),                /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) PlaylistContainer_dealloc,   /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    &PlaylistContainer_as_sequence,           /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    PlaylistContainer_str,                    /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "PlaylistContainer objects",              /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    PlaylistContainer_methods,                /* tp_methods */
    PlaylistContainer_members,                /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    PlaylistContainer_new,                    /* tp_new */
};

void
playlistcontainer_init(PyObject *module)
{
    Py_INCREF(&PlaylistContainerType);
    PyModule_AddObject(module, "PlaylistContainer",
                       (PyObject *)&PlaylistContainerType);
}
