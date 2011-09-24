#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "artist.h"

static PyMemberDef Artist_members[] = {
    {NULL}
};

static PyObject *
Artist_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    Artist *self;

    self = (Artist *) type->tp_alloc(type, 0);
    self->_artist = NULL;
    return (PyObject *)self;
}

PyObject *
Artist_FromSpotify(sp_artist * artist)
{
    PyObject *a = PyObject_CallObject((PyObject *)&ArtistType, NULL);

    ((Artist *) a)->_artist = artist;
    sp_artist_add_ref(artist);
    return a;
}

static void
Artist_dealloc(Artist * self)
{
    if (self->_artist)
        sp_artist_release(self->_artist);
    self->ob_type->tp_free(self);
}

static PyObject *
Artist_is_loaded(Artist * self)
{
    return Py_BuildValue("i", sp_artist_is_loaded(self->_artist));
}

static PyObject *
Artist_name(Artist * self)
{
    const char *s = sp_artist_name(self->_artist);

    if (!s)
        Py_RETURN_NONE;
    return PyUnicode_FromString(s);
}

static PyObject *
Artist_str(PyObject *self)
{
    Artist *a = (Artist *) self;
    const char *s = sp_artist_name(a->_artist);

    if (!s)
        Py_RETURN_NONE;
    return PyUnicode_FromString(s);
}

static PyMethodDef Artist_methods[] = {
    {"is_loaded",
     (PyCFunction)Artist_is_loaded,
     METH_NOARGS,
     "True if this artist has been loaded by the client"},
    {"name",
     (PyCFunction)Artist_name,
     METH_NOARGS,
     "Returns the name of the artist"},
    {NULL}
};

PyTypeObject ArtistType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.Artist",   /*tp_name */
    sizeof(Artist),     /*tp_basicsize */
    0,                  /*tp_itemsize */
    (destructor) Artist_dealloc,        /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    0,                  /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    Artist_str,         /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "Artist objects",   /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    Artist_methods,     /* tp_methods */
    Artist_members,     /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    Artist_new,         /* tp_new */
};

void
artist_init(PyObject *m)
{
    Py_INCREF(&ArtistType);
    PyModule_AddObject(m, "Artist", (PyObject *)&ArtistType);
}
