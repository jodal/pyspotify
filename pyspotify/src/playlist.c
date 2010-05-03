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
#include "spotify/api.h"
#include "pyspotify.h"
#include "playlist.h"
#include "track.h"

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

static PyObject *Playlist_add_callbacks(Playlist *self, PyObject *args) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
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
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
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

