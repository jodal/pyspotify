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
#include "track.h"
#include "artist.h"
#include "album.h"

static PyMemberDef Track_members[] = {
    {NULL}
};

static PyObject *Track_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Track *self;

    self = (Track *)type->tp_alloc(type, 0);
    self->_track = NULL;
    return (PyObject *)self;
}

static PyObject *Track_str(PyObject *oself) {
    Track *self = (Track *)oself;
    const char *s = sp_track_name(self->_track);
    return Py_BuildValue("s", s);
}

static PyObject *Track_is_loaded(Track *self) {
    return Py_BuildValue("i", sp_track_is_loaded(self->_track));
}

static PyObject *Track_is_available(Track *self) {
    return Py_BuildValue("i", sp_track_is_available(self->_track));
}

static PyObject *Track_artists(Track *self, PyObject *args) {
    int count = sp_track_num_artists(self->_track);
    PyObject *l = PyList_New(count);
    int i;
    for(i=0;i < count; i++) {
        Artist *a = (Artist *)PyObject_CallObject((PyObject *)&ArtistType, NULL);
        a->_artist = sp_track_artist(self->_track, i);
        PyList_SetItem(l, i, (PyObject *)a);
    }
    return l;
}

static PyObject *Track_album(Track *self) {
    Album *a = PyObject_CallObject((PyObject *)&AlbumType, NULL);
    a->_album = sp_track_album(self->_track);
    return (PyObject *)a;
}

static PyObject *Track_name(Track *self) {
    const char *s = sp_track_name(self->_track);
    return Py_BuildValue("s", s);
}

static PyObject *Track_duration(Track *self) {
    return Py_BuildValue("i", sp_track_duration(self->_track));
}

static PyObject *Track_popularity(Track *self) {
    return Py_BuildValue("i", sp_track_popularity(self->_track));
}

static PyObject *Track_disc(Track *self) {
    return Py_BuildValue("i", sp_track_disc(self->_track));
}

static PyObject *Track_index(Track *self) {
    return Py_BuildValue("i", sp_track_index(self->_track));
}

static PyObject *Track_error(Track *self) {
    return Py_BuildValue("i", sp_track_error(self->_track));
}

static PyMethodDef Track_methods[] = {
    {"is_loaded",
     (PyCFunction)Track_is_loaded,
     METH_NOARGS,
     "Get load status for this track. If the track is not loaded yet, all other functions operating on the track return default values."},
    {"is_available",
     (PyCFunction)Track_is_available,
     METH_NOARGS,
     "Return true if the track is available for playback."},
    {"artists",
     (PyCFunction)Track_artists,
     METH_VARARGS,
     "The artists who performed this track."},
    {"album",
     (PyCFunction)Track_album,
     METH_NOARGS,
     "The album of this track."},
    {"name",
     (PyCFunction)Track_name,
     METH_NOARGS,
     "The name of this track"},
    {"duration",
     (PyCFunction)Track_duration,
     METH_NOARGS,
     "The duration of this track"},
    {"popularity",
     (PyCFunction)Track_popularity,
     METH_NOARGS,
     "The popularity of this track"},
    {"disc",
     (PyCFunction)Track_disc,
     METH_NOARGS,
     "The disc number of this track"},
    {"index",
     (PyCFunction)Track_index,
     METH_NOARGS,
     "The position of this track on its disc"},
    {"error",
     (PyCFunction)Track_error,
     METH_NOARGS,
     "The error associated with this track"},
    {NULL}
};

PyTypeObject TrackType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.Track",           /*tp_name*/
    sizeof(Track),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_track_release
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
    Track_str,                  /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Track objects",            /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Track_methods,              /* tp_methods */
    Track_members,              /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    Track_new,                  /* tp_new */
};

void track_init(PyObject *m) {
    Py_INCREF(&TrackType);
    PyModule_AddObject(m, "Track", (PyObject *)&TrackType);
}
