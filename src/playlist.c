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
#include <libspotify/api.h>
#include "pyspotify.h"
#include "playlist.h"
#include "track.h"
#include "session.h"

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

static PyObject *Playlist_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Playlist *self;

    self = (Playlist *)type->tp_alloc(type, 0);
    self->_playlist = NULL;
    return (PyObject *)self;
}

static void Playlist_dealloc(Playlist *self) {
    if (self->_playlist)
        sp_playlist_release(self->_playlist);
    self->ob_type->tp_free(self);
}

static PyObject *Playlist_is_loaded(Playlist *self) {
    return Py_BuildValue("i", sp_playlist_is_loaded(self->_playlist));
}

static PyObject *Playlist_remove_tracks(Playlist *self, PyObject *args) {
    PyObject *py_tracks;
    PyObject *item;
    sp_error err;
    int *tracks;
    int num_tracks;
    int playlist_length;
    int i;

    if(!PyArg_ParseTuple(args, "O", &py_tracks))
        return NULL;
    if (!PySequence_Check(py_tracks)) {
        PyErr_SetString(PyExc_TypeError, "expected sequence");
        return NULL;
    }
    num_tracks = PySequence_Size(py_tracks);
    tracks = (int *) malloc(sizeof(tracks)*num_tracks);
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
            PyErr_SetString(PyExc_IndexError, "specified track does not exist");
            return NULL;
        }
        Py_DECREF(item);
    }
    Py_BEGIN_ALLOW_THREADS
    err = sp_playlist_remove_tracks(self->_playlist, tracks, num_tracks);
    Py_END_ALLOW_THREADS
    return handle_error(err);
}

static void pl_callbacks_table_add(Playlist *pl, playlist_callback *cb) {
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
    } else {
        cb->next = NULL;
        entry = malloc(sizeof(pl_cb_entry));
        sp_playlist_add_ref(pl->_playlist);
        entry->playlist = pl->_playlist;
        entry->callbacks = cb;
        entry->next = playlist_callbacks_table;
        playlist_callbacks_table = entry;
    }
}

static playlist_callback *pl_callbacks_table_remove(Playlist *pl,
    PyObject *callback, PyObject *userdata) {
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
    } else {
        c_curr = entry->callbacks;
        while (c_curr) {
            /* Note: a sole Python function can be represented by several
             * Python Function objects. However, to each function corresponds
             * an unique Code object.
             */
            code1 = PyFunction_GetCode(c_curr->trampoline->callback);
            code2 = PyFunction_GetCode(callback);
            if (code1 == code2 &&
                c_curr->trampoline->userdata == userdata) {
                result = c_curr;
                if (c_prev) {
                    c_prev->next = c_curr->next;
                } else {
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
       } else {
           playlist_callbacks_table = entry->next;
       }
       sp_playlist_release(entry->playlist);
       free(entry);
   }
   return result;
}

static PyObject *Playlist_add_callback(Playlist *self, PyObject *args,
    sp_playlist_callbacks *pl_callbacks) {
    PyObject *callback;
    PyObject *userdata = NULL;
    Callback *tramp;
    playlist_callback *head, *to_add;

    if(!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;
    if (userdata == NULL) {
        userdata = Py_None;
    }
    if (!(callback = as_function(callback)))
        return NULL;
    tramp = create_trampoline(callback, userdata);
    to_add = malloc(sizeof(playlist_callback));
    to_add->callback = pl_callbacks;
    to_add->trampoline = tramp;
    pl_callbacks_table_add(self, to_add);
#ifdef DEBUG
    fprintf(stderr, "[DEBUG]-playlist- adding callback (%p,%p) py(%p,%p)\n",
        pl_callbacks, tramp, PyFunction_GetCode(tramp->callback), tramp->userdata);
#endif
    sp_playlist_add_callbacks(self->_playlist, pl_callbacks, tramp);
    Py_RETURN_NONE;
}

void playlist_tracks_added_callback(sp_playlist *playlist, sp_track *const *tracks, int num_tracks, int position, void *userdata) {
    Callback *tramp = (Callback *)userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;

    gstate = PyGILState_Ensure();
    for (i = 0; i < num_tracks; i++) {
        Track *t = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
        t->_track = tracks[i];
        PyList_SetItem(py_tracks, i, (PyObject *)t);
    }
    Playlist *p = (Playlist *)PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    p->_playlist = playlist;
    Py_INCREF(p);
    PyObject_CallFunctionObjArgs(
        tramp->callback,
        p,
        py_tracks,
        Py_BuildValue("i", num_tracks),
        Py_BuildValue("i", position),
        tramp->userdata,
        NULL
    );
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *Playlist_add_tracks_added_callback(Playlist *self, PyObject *args) {
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->tracks_added = &playlist_tracks_added_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void playlist_tracks_removed_callback(sp_playlist *playlist, const int *tracks,
    int num_tracks, void *userdata) {
    Callback *tramp = (Callback *)userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;

    for (i = 0; i < num_tracks; i++) {
        PyList_SetItem(py_tracks, i, Py_BuildValue("i", tracks[i]));
    }
    gstate = PyGILState_Ensure();
    Playlist *p = (Playlist *)PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    p->_playlist = playlist;
    Py_INCREF(p);
    PyObject_CallFunctionObjArgs(
        tramp->callback,
        p,
        py_tracks,
        Py_BuildValue("i", num_tracks),
        tramp->userdata,
        NULL
    );
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *Playlist_add_tracks_removed_callback(Playlist *self, PyObject *args) {
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->tracks_removed = &playlist_tracks_removed_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

void playlist_tracks_moved_callback(sp_playlist *playlist, const int *tracks,
    int num_tracks, int new_position, void *userdata) {
    Callback *tramp = (Callback *)userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;

    for (i = 0; i < num_tracks; i++) {
        PyList_SetItem(py_tracks, i, Py_BuildValue("i", tracks[i]));
    }
    gstate = PyGILState_Ensure();
    Playlist *p = (Playlist *)PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    p->_playlist = playlist;
    Py_INCREF(p);
    PyObject_CallFunctionObjArgs(
        tramp->callback,
        p,
        py_tracks,
        Py_BuildValue("i", num_tracks),
        Py_BuildValue("i", new_position),
        tramp->userdata,
        NULL
    );
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *Playlist_add_tracks_moved_callback(Playlist *self, PyObject *args) {
    sp_playlist_callbacks *spl_callbacks;

    spl_callbacks = malloc(sizeof(sp_playlist_callbacks));
    memset(spl_callbacks, 0, sizeof(sp_playlist_callbacks));
    spl_callbacks->tracks_moved = &playlist_tracks_moved_callback;
    return Playlist_add_callback(self, args, spl_callbacks);
}

static PyObject *Playlist_remove_callback(Playlist *self, PyObject *args) {
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
        PyFunction_GetCode(callback), userdata);
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

static PyObject *Playlist_name(Playlist *self) {
    const char *name = sp_playlist_name(self->_playlist);
    return Py_BuildValue("s", name);
}

static PyObject *Playlist_rename(Playlist *self, PyObject *args) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Playlist_owner(Playlist *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Playlist_is_collaborative(Playlist *self) {
    return Py_BuildValue("i", sp_playlist_is_collaborative(self->_playlist));
}

static PyObject *Playlist_set_collaborative(Playlist *self, PyObject *args) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

/////////////// SEQUENCE PROTOCOL

Py_ssize_t Playlist_sq_length(PyObject *o) {
    Playlist *self = (Playlist *)o;
    return sp_playlist_num_tracks(self->_playlist);
}

PyObject *Playlist_sq_item(PyObject *o, Py_ssize_t index) {
    Playlist *self = (Playlist *)o;
    if(index >= sp_playlist_num_tracks(self->_playlist)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    sp_track *tr = sp_playlist_track(self->_playlist, (int)index);
    Track *t = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
    Py_INCREF(t);
    t->_track = tr;
    return (PyObject *)t;
}

int Playlist_sq_ass_item(PyObject *o, Py_ssize_t index, PyObject *args) {
    Playlist *self = (Playlist *)o;
    return 0;
}

/////////////// ADDITIONAL METHODS

static PyObject *Playlist_str(PyObject *o) {
    Playlist *self = (Playlist *)o;
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
    {"remove_callback",
    (PyCFunction)Playlist_remove_callback,
    METH_VARARGS,
    ""},
    {"name",
     (PyCFunction)Playlist_name,
     METH_NOARGS,
     "Returns the name of the playlist"},
    {NULL}
};

static PySequenceMethods Playlist_as_sequence = {
    Playlist_sq_length,		// sq_length
    0,				// sq_concat
    0,				// sq_repeat
    Playlist_sq_item,		// sq_item
    0, //Playlist_sq_ass_item,	// sq_ass_item
    0,				// sq_contains
    0,				// sq_inplace_concat
    0,				// sq_inplace_repeat
};

PyTypeObject PlaylistType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.Playlist",        /*tp_name*/
    sizeof(Playlist),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Playlist_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    &Playlist_as_sequence,      /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    Playlist_str,                 /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Playlist objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Playlist_methods,             /* tp_methods */
    Playlist_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    Playlist_new,                 /* tp_new */
};

void playlist_init(PyObject *m) {
    Py_INCREF(&PlaylistType);
    PyModule_AddObject(m, "Playlist", (PyObject *)&PlaylistType);
}
