#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "artist.h"

static PyObject *
Artist_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Artist_SP_ARTIST(self) = NULL;
    return self;
}

PyObject *
Artist_FromSpotify(sp_artist *artist)
{
    PyObject *self = ArtistType.tp_alloc(&ArtistType, 0);
    Artist_SP_ARTIST(self) = artist;
    sp_artist_add_ref(artist);
    return self;
}

static void
Artist_dealloc(PyObject *self)
{
    if (Artist_SP_ARTIST(self) != NULL)
        sp_artist_release(Artist_SP_ARTIST(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Artist_is_loaded(PyObject *self)
{
    return PyBool_FromLong(sp_artist_is_loaded(Artist_SP_ARTIST(self)));
}

static PyObject *
Artist_name(PyObject *self)
{
    const char *name = sp_artist_name(Artist_SP_ARTIST(self));
    if (name == NULL)
        Py_RETURN_NONE;
    return PyUnicode_FromString(name);
}

static PyObject *
Artist_str(PyObject *self)
{
    return Artist_name(self);
}

static PyMethodDef Artist_methods[] = {
    {"is_loaded", (PyCFunction)Artist_is_loaded, METH_NOARGS,
     "True if this artist has been loaded by the client"
    },
    {"name", (PyCFunction)Artist_name, METH_NOARGS,
     "Returns the name of the artist"
    },
    {NULL}
};

static PyMemberDef Artist_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject ArtistType = {
    PyObject_HEAD_INIT(NULL) 0,                /*ob_size*/
    "spotify.Artist",                          /*tp_name*/
    sizeof(Artist),                            /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    (destructor) Artist_dealloc,               /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    0,                                         /*tp_as_sequence*/
    0,                                         /*tp_as_mapping*/
    0,                                         /*tp_hash*/
    0,                                         /*tp_call*/
    Artist_str,                                /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "Artist objects",                          /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    Artist_methods,                            /* tp_methods */
    Artist_members,                            /* tp_members */
    0,                                         /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    Artist_new,                                /* tp_new */
};

void
artist_init(PyObject *module)
{
    if (PyType_Ready(&ArtistType) < 0)
        return;

    Py_INCREF(&ArtistType);
    PyModule_AddObject(module, "Artist", (PyObject *)&ArtistType);
}
