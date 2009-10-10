#include <Python.h>
#include <structmember.h>
#include "spotify/api.h"
#include "pyspotify.h"

static PyObject *TrackError;

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
    // TODO: make this prettier
    const char *s = sp_track_name(self->_track);
    return Py_BuildValue("s", s);
}

static PyObject *Track_is_loaded(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_is_available(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_num_artists(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_artist(Track *self, PyObject *args) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_album(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_name(Track *self) {
    const char *s = sp_track_name(self->_track);
    return Py_BuildValue("s", s);
}

static PyObject *Track_duration(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_popularity(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_disc(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
}

static PyObject *Track_index(Track *self) {
    PyErr_SetString(PyExc_NotImplementedError, "");
    return NULL;
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
    {"num_artists",
     (PyCFunction)Track_num_artists,
     METH_NOARGS,
     "The number of artists performing on this track"},
    {"artist",
     (PyCFunction)Track_artist,
     METH_VARARGS,
     "The artist matching the specified index performing on this track."},
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
    {NULL}
};

static PyTypeObject TrackType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.track.Track",       /*tp_name*/
    sizeof(Track),              /*tp_basicsize*/
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

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC inittrack(void) {
    PyObject *m;

    if(PyType_Ready(&TrackType) < 0)
	return;

    m = Py_InitModule("track", module_methods);
    if(m == NULL)
        return;

    PyEval_InitThreads();
    TrackError = PyErr_NewException("spotify.track.TrackError", NULL, NULL);
    Py_INCREF(TrackError);
    PyModule_AddObject(m, "TrackError", TrackError);
    PyModule_AddObject(m, "Track", (PyObject *)&TrackType);
}
