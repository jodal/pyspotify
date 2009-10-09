#include <Python.h>
#include <structmember.h>
#include "spotify/api.h"

static PyObject *AlbumError;
static PyTypeObject AlbumType;

typedef struct {
    PyObject_HEAD
    sp_album *_album;
} Album;

static PyMemberDef Album_members[] = {
    {NULL}
};

static PyObject *Album_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Album *self;

    self = (Album *)type->tp_alloc(type, 0);
    self->_album = NULL;
    return (PyObject *)self;
}

static PyObject *Album_is_loaded(Album *self) {
}

static PyObject *Album_is_available(Album *self) {
}

static PyObject *Album_artist(Album *self) {
}

static PyObject *Album_cover(Album *self) {
}

static PyObject *Album_name(Album *self) {
}

static PyObject *Album_year(Album *self) {
}

static PyObject *Album_type(Album *self) {
}

static PyObject *Album_str(Album *self) {
}

static PyMethodDef Album_methods[] = {
    {"is_loaded",
     (PyCFunction)Album_is_loaded,
     METH_NOARGS,
     "True if this album has been loaded by the client"},
    {"is_available",
     (PyCFunction)Album_is_available,
     METH_NOARGS,
     "True if the album is available"},
    {"artist",
     (PyCFunction)Album_artist,
     METH_NOARGS,
     "Returns the artist associated with this album"},
    {"cover",
     (PyCFunction)Album_cover,
     METH_NOARGS,
     "Returns the cover data associated with this album"},
    {"name",
     (PyCFunction)Album_name,
     METH_NOARGS,
     "Returns the name of the album"},
    {"year",
     (PyCFunction)Album_year,
     METH_NOARGS,
     "Returns the year in which the album was released"},
    {"type",
     (PyCFunction)Album_type,
     METH_NOARGS,
     "Returns the type of the album, one of TYPE_ALBUM, TYPE_SINGLE, TYPE_COMPILATION or TYPE_UNKNOWN"},
    {NULL}
};

static PyTypeObject AlbumType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.album.Album",     /*tp_name*/
    sizeof(Album),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_album_release
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
    Album_str,                 /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Album objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Album_methods,             /* tp_methods */
    Album_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,			       /* tp_init */
    0,                         /* tp_alloc */
    Album_new,                 /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initalbum(void) {
    PyObject *m;

    if(PyType_Ready(&AlbumType) < 0)
	return;

    m = Py_InitModule("album", module_methods);
    if(m == NULL)
        return;

    PyEval_InitThreads();
    AlbumError = PyErr_NewException("spotify.album.AlbumError", NULL, NULL);
    Py_INCREF(AlbumError);
    PyModule_AddObject(m, "AlbumError", AlbumError);
    PyModule_AddObject(m, "Album", (PyObject *)&AlbumType);
}
