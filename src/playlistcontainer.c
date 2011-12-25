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

static PyMemberDef PlaylistContainer_members[] = {
    {NULL}
};

static PyObject *
PlaylistContainer_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    PlaylistContainer *self;

    self = (PlaylistContainer *) type->tp_alloc(type, 0);
    self->_playlistcontainer = NULL;
    return (PyObject *)self;
}

PyObject *
PlaylistContainer_FromSpotify(sp_playlistcontainer * container)
{
    PyObject *pc =
        PyObject_CallObject((PyObject *)&PlaylistContainerType, NULL);
    ((PlaylistContainer *) pc)->_playlistcontainer = container;
    sp_playlistcontainer_add_ref(container);
    return pc;
}

static void
PlaylistContainer_dealloc(PlaylistContainer * self)
{
    if (self->_playlistcontainer)
        sp_playlistcontainer_release(self->_playlistcontainer);
    self->ob_type->tp_free(self);
}

static void
plc_callbacks_table_add(PlaylistContainer * plc,
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
        entry = malloc(sizeof(plc_cb_entry));
        sp_playlistcontainer_add_ref(plc->_playlistcontainer);
        entry->playlistcontainer = plc->_playlistcontainer;
        entry->callbacks = cb;
        entry->next = playlistcontainer_callbacks_table;
        playlistcontainer_callbacks_table = entry;
    }
}

static PyObject *
PlaylistContainer_add_callback(PlaylistContainer * self,
                               PyObject *args,
                               sp_playlistcontainer_callbacks * plc_callbacks)
{
    PyObject *callback, *userdata = NULL;
    Callback *tramp;
    playlistcontainer_callback *to_add;

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
    to_add = malloc(sizeof(playlistcontainer_callback));
    to_add->callback = plc_callbacks;
    to_add->trampoline = tramp;
    plc_callbacks_table_add(self, to_add);
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-plcontainer- adding callback (%p,%p) py(%p,%p)\n",
            plc_callbacks, tramp, tramp->callback, tramp->userdata);
#endif
    sp_playlistcontainer_add_callbacks(self->_playlistcontainer, plc_callbacks,
                                       tramp);
    Py_RETURN_NONE;
}

void
playlistcontainer_loaded_callback(sp_playlistcontainer * playlistcontainer,
                                  void *userdata)
{
    Callback *tramp = (Callback *) userdata;
    PyGILState_STATE gstate;
    PyObject *res, *pc;

    gstate = PyGILState_Ensure();
    pc = PlaylistContainer_FromSpotify(playlistcontainer);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       pc, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_DECREF(pc);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_loaded_callback(PlaylistContainer * self, PyObject *args)
{
    sp_playlistcontainer_callbacks *splc_callbacks;

    splc_callbacks = malloc(sizeof(sp_playlistcontainer_callbacks));
    memset(splc_callbacks, 0, sizeof(sp_playlistcontainer_callbacks));
    splc_callbacks->container_loaded = &playlistcontainer_loaded_callback;
    return PlaylistContainer_add_callback(self, args, splc_callbacks);
}

void
playlistcontainer_playlist_added_callback(sp_playlistcontainer *
                                          playlistcontainer,
                                          sp_playlist * playlist,
                                          int position, void *userdata)
{
    Callback *tramp;
    PyObject *pc, *p, *pos, *res;;
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    pc = PlaylistContainer_FromSpotify(playlistcontainer);
    p = Playlist_FromSpotify(playlist);
    pos = Py_BuildValue("i", position);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       pc, p, pos, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_DECREF(pc);
    Py_DECREF(p);
    Py_DECREF(pos);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_playlist_added_callback(PlaylistContainer * self,
                                              PyObject *args)
{
    sp_playlistcontainer_callbacks *splc_callbacks;

    splc_callbacks = malloc(sizeof(sp_playlistcontainer_callbacks));
    memset(splc_callbacks, 0, sizeof(sp_playlistcontainer_callbacks));
    splc_callbacks->playlist_added =
        &playlistcontainer_playlist_added_callback;
    return PlaylistContainer_add_callback(self, args, splc_callbacks);
}

void
playlistcontainer_playlist_moved_callback(sp_playlistcontainer *
                                          playlistcontainer,
                                          sp_playlist * playlist,
                                          int position, int new_position,
                                          void *userdata)
{
    Callback *tramp;
    PyObject *pc, *p, *pos, *new_pos, *res;
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    pc = PlaylistContainer_FromSpotify(playlistcontainer);
    p = Playlist_FromSpotify(playlist);
    pos = Py_BuildValue("i", position);
    new_pos = Py_BuildValue("i", new_position);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       pc,
                                       p, pos, new_pos, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_DECREF(pc);
    Py_DECREF(p);
    Py_DECREF(pos);
    Py_DECREF(new_pos);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_playlist_moved_callback(PlaylistContainer * self,
                                              PyObject *args)
{
    sp_playlistcontainer_callbacks *splc_callbacks;

    splc_callbacks = malloc(sizeof(sp_playlistcontainer_callbacks));
    memset(splc_callbacks, 0, sizeof(sp_playlistcontainer_callbacks));
    splc_callbacks->playlist_moved =
        &playlistcontainer_playlist_moved_callback;
    return PlaylistContainer_add_callback(self, args, splc_callbacks);
}

void
playlistcontainer_playlist_removed_callback(sp_playlistcontainer *
                                            playlistcontainer,
                                            sp_playlist * playlist,
                                            int position, void *userdata)
{
    Callback *tramp;
    PyObject *pc, *p, *pos, *res;
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    tramp = (Callback *) userdata;
    pc = PlaylistContainer_FromSpotify(playlistcontainer);
    p = Playlist_FromSpotify(playlist);
    pos = Py_BuildValue("i", position);
    res = PyObject_CallFunctionObjArgs(tramp->callback,
                                       pc, p, pos, tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    Py_DECREF(pc);
    Py_DECREF(p);
    Py_DECREF(pos);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
}

static PyObject *
PlaylistContainer_add_playlist_removed_callback(PlaylistContainer * self,
                                                PyObject *args)
{
    sp_playlistcontainer_callbacks *splc_callbacks;

    splc_callbacks = malloc(sizeof(sp_playlistcontainer_callbacks));
    memset(splc_callbacks, 0, sizeof(sp_playlistcontainer_callbacks));
    splc_callbacks->playlist_removed =
        &playlistcontainer_playlist_removed_callback;
    return PlaylistContainer_add_callback(self, args, splc_callbacks);
}

static PyObject *
PlaylistContainer_str(PyObject *o)
{
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

Py_ssize_t
PlaylistContainer_sq_length(PyObject *o)
{
    PlaylistContainer *self = (PlaylistContainer *) o;

    return sp_playlistcontainer_num_playlists(self->_playlistcontainer);
}

static PyObject *
PlaylistContainer_add_new_playlist(PlaylistContainer *pc, PyObject *args)
{
    char *name = NULL;
    int len;
    sp_playlist *playlist;

    if (!sp_playlistcontainer_is_loaded(pc->_playlistcontainer)) {
        PyErr_SetString(SpotifyError, "PlaylistContainer not loaded");
        return NULL;
    }
    if (!PyArg_ParseTuple(args, "es#", ENCODING, &name, &len))
        return NULL;
    if (len > 255) {
        PyErr_SetString(PyExc_ValueError,
                "Playlist name must be < 255 characters long");
        goto error;
    }
    playlist =
        sp_playlistcontainer_add_new_playlist(pc->_playlistcontainer, name);
    if (!playlist) {
        PyErr_SetString(SpotifyError, "Operation failed.");
        goto error;
    }
    return Playlist_FromSpotify(playlist);

    error:
        PyMem_Free(name);
        return NULL;
}

/// PlaylistContainer Get Item []
PyObject *
PlaylistContainer_sq_item(PyObject *o, Py_ssize_t index)
{
    PlaylistContainer *pc = (PlaylistContainer *) o;
    PyObject *p;
    sp_playlist_type type;

    if (index >= sp_playlistcontainer_num_playlists(pc->_playlistcontainer)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    type = sp_playlistcontainer_playlist_type(pc->_playlistcontainer, (int)index);
    if (type == SP_PLAYLIST_TYPE_PLAYLIST) {
        p = Playlist_FromSpotify(sp_playlistcontainer_playlist(
                    pc->_playlistcontainer, (int)index));
    }
    else {
        p = PlaylistFolder_FromSpotify(pc->_playlistcontainer,
                                                (int)index, type);
    }
    return p;
}

/// PlaylistContainer Set Item [] =
PyObject *
PlaylistContainer_sq_ass_item(PyObject *o, Py_ssize_t index, Py_ssize_t meh)
{
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

PySequenceMethods PlaylistContainer_as_sequence = {
    PlaylistContainer_sq_length,        // sq_length
    0,                  // sq_concat
    0,                  // sq_repeat
    PlaylistContainer_sq_item,  // sq_item
    PlaylistContainer_sq_ass_item,      // sq_ass_item
    0,                  // sq_contains
    0,                  // sq_inplace_concat
    0,                  // sq_inplace_repeat
};

static PyMethodDef PlaylistContainer_methods[] = {
    {"add_loaded_callback",
     (PyCFunction)PlaylistContainer_add_loaded_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_added_callback",
     (PyCFunction)PlaylistContainer_add_playlist_added_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_moved_callback",
     (PyCFunction)PlaylistContainer_add_playlist_moved_callback,
     METH_VARARGS,
     ""},
    {"add_playlist_removed_callback",
     (PyCFunction)PlaylistContainer_add_playlist_removed_callback,
     METH_VARARGS,
     ""},
    {"add_new_playlist",
     (PyCFunction)PlaylistContainer_add_new_playlist,
     METH_VARARGS,
     "Add a new empty playlist to the playlist container."},
    {NULL}
};

PyTypeObject PlaylistContainerType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.PlaylistContainer",        /*tp_name */
    sizeof(PlaylistContainer),  /*tp_basicsize */
    0,                  /*tp_itemsize */
    (destructor) PlaylistContainer_dealloc,     /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    &PlaylistContainer_as_sequence,     /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    PlaylistContainer_str,      /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "PlaylistContainer objects",        /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    PlaylistContainer_methods,  /* tp_methods */
    PlaylistContainer_members,  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    PlaylistContainer_new,      /* tp_new */
};

void
playlistcontainer_init(PyObject *m)
{
    Py_INCREF(&PlaylistContainerType);
    PyModule_AddObject(m, "PlaylistContainer",
                       (PyObject *)&PlaylistContainerType);
}
