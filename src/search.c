#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "search.h"
#include "artist.h"
#include "album.h"
#include "track.h"

static PyObject *
Results_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Results_SP_SEARCH(self) = NULL;
    return self;
}

PyObject *
Results_FromSpotify(sp_search * search)
{
    PyObject *self = ResultsType.tp_alloc(&ResultsType, 0);
    Results_SP_SEARCH(self) = search;
    sp_search_add_ref(search);
    return self;
}

static void
Results_dealloc(PyObject *self)
{
    if (Results_SP_SEARCH(self) != NULL)
        sp_search_release(Results_SP_SEARCH(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Results_is_loaded(PyObject *self)
{
    return PyBool_FromLong(sp_search_is_loaded(Results_SP_SEARCH(self)));
}

static PyObject *
Results_did_you_mean(PyObject *self)
{
    const char *did_you_mean = sp_search_did_you_mean(Results_SP_SEARCH(self));
    return PyUnicode_FromString(did_you_mean);
}

static PyObject *
Results_error(PyObject *self)
{
    /* TODO: return enums that represent sp_error */
    sp_error error = sp_search_error(Results_SP_SEARCH(self));
    return Py_BuildValue("i", error);
}

static PyObject *
Results_artists(PyObject *self)
{
    sp_artist *artist;
    int i;
    int count = sp_search_num_artists(Results_SP_SEARCH(self));
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        artist = sp_search_artist(Results_SP_SEARCH(self), i);
        PyList_SetItem(list, i, Artist_FromSpotify(artist));
    }
    return list;
}

static PyObject *
Results_albums(PyObject *self)
{
    sp_album *album;
    int i;
    int count = sp_search_num_albums(Results_SP_SEARCH(self));
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        album = sp_search_album(Results_SP_SEARCH(self), i);
        PyList_SetItem(list, i, Album_FromSpotify(album));
    }
    return list;
}

static PyObject *
Results_tracks(PyObject *self)
{
    sp_track *track;
    int i;
    int count = sp_search_num_tracks(Results_SP_SEARCH(self));
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        track = sp_search_track(Results_SP_SEARCH(self), i);
        PyList_SetItem(list, i, Track_FromSpotify(track));
    }
    return list;
}

static PyObject *
Results_total_albums(PyObject *self)
{
    return Py_BuildValue("i", sp_search_total_albums(Results_SP_SEARCH(self)));
}

static PyObject *
Results_total_artists(PyObject *self)
{
    return Py_BuildValue("i", sp_search_total_artists(Results_SP_SEARCH(self)));
}

static PyObject *
Results_total_tracks(PyObject *self)
{
    return Py_BuildValue("i", sp_search_total_tracks(Results_SP_SEARCH(self)));
}

static PyObject *
Results_query(PyObject *self)
{
    return PyUnicode_FromString(sp_search_query(Results_SP_SEARCH(self)));
}

PyObject *
Results_str(PyObject * self)
{
    return Results_query(self);
}

static PyMethodDef Results_methods[] = {
    {"is_loaded", (PyCFunction)Results_is_loaded, METH_NOARGS,
     "True if these results have been loaded"
    },
    {"did_you_mean", (PyCFunction)Results_did_you_mean, METH_NOARGS,
     "True if this results has been loaded by the client"
    },
    {"error", (PyCFunction)Results_error, METH_NOARGS,
     "True if this results has been loaded by the client"
    },
    {"artists", (PyCFunction)Results_artists, METH_NOARGS,
     "Return a list of all the artists found by the search"
    },
    {"albums", (PyCFunction)Results_albums, METH_NOARGS,
     "Return a list of all the albums found by the search"
    },
    {"tracks", (PyCFunction)Results_tracks, METH_NOARGS,
     "Return a list of all the tracks found by the search"
    },
    {"total_albums", (PyCFunction)Results_total_albums, METH_NOARGS,
     "Return the total number of albums available from this search - if this " \
     "is more than the number in 'albums' then more are available that were " \
     "not requested"
    },
    {"total_artists", (PyCFunction)Results_total_artists, METH_NOARGS,
     "Return the total number of artists available from this search - if this " \
     "is more than the number in 'artists' then more are available that were " \
     "not requested"
    },
    {"total_tracks", (PyCFunction)Results_total_tracks, METH_NOARGS,
     "Return the total number of tracks available from this search - if this " \
      "is more than the number in 'tracks' then more are available that were " \
      "not requested"
    },
    {"query", (PyCFunction)Results_query, METH_NOARGS,
     "The query expression that generated these results"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Results_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject ResultsType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Results",                        /*tp_name*/
    sizeof(Results),                          /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)Results_dealloc,              /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash*/
    0,                                        /*tp_call*/
    Results_str,                              /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Results objects",                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Results_methods,                          /* tp_methods */
    Results_members,                          /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Results_new,                              /* tp_new */
};

void
search_init(PyObject *module)
{
    Py_INCREF(&ResultsType);
    PyModule_AddObject(module, "Results", (PyObject *)&ResultsType);
}
