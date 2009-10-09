art#include <Python.h>
#include <structmember.h>
#include "spotify/api.h"

static PyObject *PlaylistError;
static PyTypeObject PlaylistType;

typedef struct {
    PyObject_HEAD
    sp_playlist *_playlist;
} Playlist;

typedef struct {
    PyObject_HEAD
    sp_playlistcontainer *_playlistcontainer;
} PlaylistContainer;

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
}

static PyObject *Playlist_add_callbacks(Playlist *self, PyObject *args) {
}

static PyObject *Playlist_remove_callbacks(Playlist *self, PyObject *args) {
}

static PyObject *Playlist_name(Playlist *self) {
}

static PyObject *Playlist_rename(Playlist *self, PyObject *args) {
}

static PyObject *Playlist_owner(Playlist *self) {
}

static PyObject *Playlist_is_collaborative(Playlist *self) {
}

static PyObject *Playlist_set_collaborative(Playlist *self, PyObject *args) {
}

/////////////// SEQUENCE PROTOCOL

int PySequence_Check(


/////////////// ADDITIONAL METHODS

static PyObject *Playlist_str(Playlist *self) {
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
    Playlist_sq_ass_item,	// sq_ass_item
    0,				// sq_contains
    0,				// sq_inplace_concat
    0,				// sq_inplace_repeat
};

static PyTypeObject PlaylistType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.playlist.Playlist",     /*tp_name*/
    sizeof(Playlist),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/  // TODO: IMPLEMENT THIS WITH sp_playlist_release
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    Playlist_as_sequence,      /*tp_as_sequence*/
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


static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initplaylist(void) {
    PyObject *m;

    if(PyType_Ready(&PlaylistType) < 0)
	return;

    m = Py_InitModule("playlist", module_methods);
    if(m == NULL)
        return;

    PyEval_InitThreads();
    PlaylistError = PyErr_NewException("spotify.playlist.PlaylistError", NULL, NULL);
    Py_INCREF(PlaylistError);
    PyModule_AddObject(m, "PlaylistError", PlaylistError);
    PyModule_AddObject(m, "Playlist", (PyObject *)&PlaylistType);
}
