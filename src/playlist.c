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
#include "libspotify/api.h"
#include "pyspotify.h"
#include "playlist.h"
#include "track.h"
#include "session.h"

static PyMemberDef Playlist_members[] = {
    {NULL}
};

static PyMemberDef PlaylistContainer_members[] = {
    {NULL}
};

static PyObject *Playlist_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Playlist *self;

    self = (Playlist *)type->tp_alloc(type, 0);
    self->_playlist = NULL;
    return (PyObject *)self;
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

typedef struct {
    PyObject *callback;
    PyObject *userdata;
} playlist_callback_trampoline;

static PyObject *Playlist__add_callback(Playlist *self, PyObject *args, sp_playlist_callbacks pl_callbacks) {
    PyObject *callback;
    PyObject *userdata = NULL;
    playlist_callback_trampoline *tramp;
    if(!PyArg_ParseTuple(args, "O|O", &callback, &userdata))
        return NULL;
    if (userdata == NULL) {
        userdata = (PyObject *)Py_None;
        Py_INCREF(Py_None);
    }
    Py_INCREF(callback);
    Py_INCREF(userdata);
    tramp = malloc(sizeof(playlist_callback_trampoline));
    tramp->userdata = userdata;
    tramp->callback = callback;
    Py_BEGIN_ALLOW_THREADS
    sp_playlist_add_callbacks(self->_playlist, &pl_callbacks, tramp);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

void playlist_tracks_added_callback(sp_playlist *playlist, sp_track *const *tracks, int num_tracks, int position, void *userdata) {
    playlist_callback_trampoline *tramp = (playlist_callback_trampoline *)userdata;
    PyGILState_STATE gstate;
    PyObject *py_tracks = PyList_New(num_tracks);
    int i;
    for (i = 0; i < num_tracks; i++) {
        Track *t = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
        t->_track = tracks[i];
        PyList_SetItem(py_tracks, i, (PyObject *)t);
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
        Py_BuildValue("i", position),
        tramp->userdata,
        NULL
    );
    Py_DECREF(py_tracks);
    Py_DECREF(p);
    PyGILState_Release(gstate);
}

static PyObject *Playlist_add_tracks_added_callback(Playlist *self, PyObject *args) {
    sp_playlist_callbacks pl_callbacks = {
        .tracks_added = &playlist_tracks_added_callback
    };
    return Playlist__add_callback(self, args, pl_callbacks);
}

void playlist_tracks_removed_callback(sp_playlist *playlist, const int *tracks, int num_tracks, void *userdata) {
    playlist_callback_trampoline *tramp = (playlist_callback_trampoline *)userdata;
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
    sp_playlist_callbacks pl_callbacks = {
        .tracks_removed = &playlist_tracks_removed_callback
    };
    return Playlist__add_callback(self, args, pl_callbacks);
}

void playlist_tracks_moved_callback(sp_playlist *playlist, const int *tracks, int num_tracks, int new_position, void *userdata) {
    playlist_callback_trampoline *tramp = (playlist_callback_trampoline *)userdata;
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
    sp_playlist_callbacks pl_callbacks = {
        .tracks_moved = &playlist_tracks_moved_callback
    };
    return Playlist__add_callback(self, args, pl_callbacks);
}

static PyObject *Playlist_remove_callbacks(Playlist *self, PyObject *args) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
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
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_playlist_release
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

static PyObject *PlaylistContainer_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PlaylistContainer *self;

    self = (PlaylistContainer *)type->tp_alloc(type, 0);
    self->_playlistcontainer = NULL;
    return (PyObject *)self;
}

static PyMethodDef PlaylistContainer_methods[] = {
    {NULL}
};

static PyObject *PlaylistContainer_str(PyObject *o) {
    Playlist *self = (Playlist *)o;
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

Py_ssize_t PlaylistContainer_sq_length(PyObject *o) {
    PlaylistContainer *self = (PlaylistContainer *)o;
    return sp_playlistcontainer_num_playlists(self->_playlistcontainer);
}

/// PlaylistContainer Get Item []
PyObject *PlaylistContainer_sq_item(PyObject *o, Py_ssize_t index) {
    PlaylistContainer *pc = (PlaylistContainer *)o;
    if(index >= sp_playlistcontainer_num_playlists(pc->_playlistcontainer)) {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
    sp_playlist *pl = sp_playlistcontainer_playlist(pc->_playlistcontainer, (int)index);
    Playlist *p = (Playlist *)PyObject_CallObject((PyObject *)&PlaylistType, NULL);
    Py_INCREF(p);
    p->_playlist = pl;
    return (PyObject *)p;
}

/// PlaylistContainer Set Item [] =
PyObject *PlaylistContainer_sq_ass_item(PyObject *o, Py_ssize_t index, Py_ssize_t meh) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

PySequenceMethods PlaylistContainer_as_sequence = {
    PlaylistContainer_sq_length,		// sq_length
    0,						// sq_concat
    0,						// sq_repeat
    PlaylistContainer_sq_item,			// sq_item
    PlaylistContainer_sq_ass_item,		// sq_ass_item
    0,						// sq_contains
    0,						// sq_inplace_concat
    0,						// sq_inplace_repeat
};

PyTypeObject PlaylistContainerType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.playlist.PlaylistContainer",     /*tp_name*/
    sizeof(PlaylistContainer),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_playlist_release
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    &PlaylistContainer_as_sequence,      /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    PlaylistContainer_str,                 /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "PlaylistContainer objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    PlaylistContainer_methods,             /* tp_methods */
    PlaylistContainer_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    PlaylistContainer_new,                 /* tp_new */
};

void playlist_init(PyObject *m) {
    Py_INCREF(&PlaylistType);
    Py_INCREF(&PlaylistContainerType);
    PyModule_AddObject(m, "Playlist", (PyObject *)&PlaylistType);
    PyModule_AddObject(m, "PlaylistContainer", (PyObject *)&PlaylistContainerType);
}

