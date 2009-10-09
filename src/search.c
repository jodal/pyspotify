#include <Python.h>
#include <structmember.h>
#include "spotify/api.h"

static PyObject *ResultsError;
static PyTypeObject ResultsType;

typedef struct {
    PyObject_HEAD
    sp_search *_search;
} Results;

static PyMemberDef Results_members[] = {
    {NULL}
};

static PyObject *Results_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Results *self;

    self = (Results *)type->tp_alloc(type, 0);
    self->_search = NULL;
    return (PyObject *)self;
}

static PyObject *Results_did_you_mean(Results *self) {
}

static PyObject *Results_error(Results *self) {
}

static PyObject *Results_artists(Results *self) {
}

static PyObject *Results_albums(Results *self) {
}

static PyObject *Results_tracks(Results *self) {
}

static PyObject *Results_total_tracks(Results *self) {
}

static PyObject *Results_query(Results *self) {
}

static PyObject *Results_str(Results *self) {
}

static PyMethodDef Results_methods[] = {
    {"is_loaded",
     (PyCFunction)Results_is_loaded,
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

static PyTypeObject ResultsType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spotify.search.Results",     /*tp_name*/
    sizeof(Results),             /*tp_basicsize*/
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

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initresults(void) {
    PyObject *m;

    if(PyType_Ready(&ResultsType) < 0)
	return;

    m = Py_InitModule("results", module_methods);
    if(m == NULL)
        return;

    PyEval_InitThreads();
    ResultsError = PyErr_NewException("spotify.search.ResultsError", NULL, NULL);
    Py_INCREF(ResultsError);
    PyModule_AddObject(m, "ResultsError", ResultsError);
    PyModule_AddObject(m, "Results", (PyObject *)&ResultsType);
}
