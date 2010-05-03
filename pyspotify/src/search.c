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
#include "search.h"
#include "artist.h"
#include "album.h"
#include "track.h"

static PyMemberDef Results_members[] = {
    {NULL}
};

static PyObject *Results_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Results *self;
    self = (Results *)type->tp_alloc(type, 0);
    self->_search = NULL;
    return (PyObject *)self;
}

static PyObject *Results_is_loaded(Results *self) {
    return Py_BuildValue("i", sp_search_is_loaded(self->_search));
}

static PyObject *Results_did_you_mean(Results *self) {
    return PyString_FromString(sp_search_did_you_mean(self->_search));
}

static PyObject *Results_error(Results *self) {
    return Py_BuildValue("i", sp_search_error(self->_search));
}

static PyObject *Results_artists(Results *self) {
    int count = sp_search_num_artists(self->_search);
    PyObject *l = PyList_New(count);
    int i;
    for(i=0;i<count;++i) {
        Artist *a = (Artist *)PyObject_CallObject((PyObject *)&ArtistType, NULL);
        a->_artist = sp_search_artist(self->_search, i);
        PyList_SetItem(l, i, (PyObject *)a);
    }
    Py_INCREF(l);
    return l;
}

static PyObject *Results_albums(Results *self) {
    int count = sp_search_num_albums(self->_search);
    PyObject *l = PyList_New(count);
    int i;
    for(i=0;i<count;++i) {
        Album *a = (Album *)PyObject_CallObject((PyObject *)&AlbumType, NULL);
        a->_album = sp_search_album(self->_search, i);
        PyList_SetItem(l, i, (PyObject *)a);
    }
    Py_INCREF(l);
    return l;
}

static PyObject *Results_tracks(Results *self) {
    int count = sp_search_num_tracks(self->_search);
    PyObject *l = PyList_New(count);
    int i;
    for(i=0;i<count;++i) {
        Track *a = (Track *)PyObject_CallObject((PyObject *)&TrackType, NULL);
        a->_track = sp_search_track(self->_search, i);
        PyList_SetItem(l, i, (PyObject *)a);
    }
    Py_INCREF(l);
    return l;
}

static PyObject *Results_total_tracks(Results *self) {
    return Py_BuildValue("i", sp_search_total_tracks(self->_search));
}

static PyObject *Results_query(Results *self) {
    return PyString_FromString(sp_search_query(self->_search));
}

PyObject *Results_str(PyObject *self) {
    return PyString_FromString(sp_search_query(((Results *)self)->_search));
}

static PyMethodDef Results_methods[] = {
    {"is_loaded",
     (PyCFunction)Results_is_loaded,
     METH_NOARGS,
     "True if these results have been loaded"},
    {"did_you_mean",
     (PyCFunction)Results_did_you_mean,
     METH_NOARGS,
     "True if this results has been loaded by the client"},
    {"error",
     (PyCFunction)Results_error,
     METH_NOARGS,
     "True if this results has been loaded by the client"},
    {"artists",
     (PyCFunction)Results_artists,
     METH_NOARGS,
     "Return a list of all the artists found by the search"},
    {"albums",
     (PyCFunction)Results_albums,
     METH_NOARGS,
     "Return a list of all the albums found by the search"},
    {"tracks",
     (PyCFunction)Results_tracks,
     METH_NOARGS,
     "Return a list of all the tracks found by the search"},
    {"total_tracks",
     (PyCFunction)Results_total_tracks,
     METH_NOARGS,
     "Return the total number of tracks available from this search - if this is more than the number in 'tracks' then more are available that were not requested"},
    {"query",
     (PyCFunction)Results_query,
     METH_NOARGS,
     "The query expression that generated these results"},
    {NULL}
};

PyTypeObject ResultsType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.Results",         /*tp_name*/
    sizeof(Results),           /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_results_release
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
    Results_str,                 /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Results objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Results_methods,             /* tp_methods */
    Results_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    Results_new,                 /* tp_new */
};

void search_init(PyObject *m) {
    PyModule_AddObject(m, "Results", (PyObject *)&ResultsType);
    Py_INCREF(&ResultsType);
}
