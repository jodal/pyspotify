#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "album.h"
#include "artist.h"

static PyObject *
Album_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Album_SP_ALBUM(self) = NULL;
    return self;
}

PyObject *
Album_FromSpotify(sp_album *album)
{
    PyObject *self = AlbumType.tp_alloc(&AlbumType, 0);
    Album_SP_ALBUM(self) = album;
    sp_album_add_ref(album);
    return self;
}

static void
Album_dealloc(PyObject *self)
{
    if (Album_SP_ALBUM(self) != NULL)
        sp_album_release(Album_SP_ALBUM(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Album_is_loaded(PyObject *self)
{
    bool loaded = sp_album_is_loaded(Album_SP_ALBUM(self));
    return PyBool_FromLong(loaded);
}

static PyObject *
Album_is_available(PyObject *self)
{
    bool available = sp_album_is_available(Album_SP_ALBUM(self));
    return PyBool_FromLong(available);
}

static PyObject *
Album_artist(PyObject *self)
{
    sp_artist *artist = sp_album_artist(Album_SP_ALBUM(self));
    if (artist == NULL)
        Py_RETURN_NONE;

    return Artist_FromSpotify(artist);
}

static PyObject *
Album_cover(PyObject *self)
{
    const byte *cover = sp_album_cover(
        Album_SP_ALBUM(self), SP_IMAGE_SIZE_NORMAL);
    if (cover == NULL)
        Py_RETURN_NONE;
    return Py_BuildValue("s#", cover, 20);
}

static PyObject *
Album_name(PyObject *self)
{
    return PyUnicode_FromString(sp_album_name(Album_SP_ALBUM(self)));
}

static PyObject *
Album_year(PyObject *self)
{
    return Py_BuildValue("i", sp_album_year(Album_SP_ALBUM(self)));
}

static PyObject *
Album_type(PyObject *self)
{
    /* TODO: return enums that represent sp_albumtype */
    sp_albumtype album_type = sp_album_type(Album_SP_ALBUM(self));
    return Py_BuildValue("i", album_type);
}

static PyObject *
Album_str(PyObject *self)
{
    return Album_name(self);
}

static PyMethodDef Album_methods[] = {
    {"is_loaded", (PyCFunction)Album_is_loaded, METH_NOARGS,
     "True if this album has been loaded by the client"
    },
    {"is_available", (PyCFunction)Album_is_available, METH_NOARGS,
     "True if the album is available"
    },
    {"artist", (PyCFunction)Album_artist, METH_NOARGS,
     "Returns the artist associated with this album"
    },
    {"cover", (PyCFunction)Album_cover, METH_NOARGS,
     "Returns the cover data associated with this album"
    },
    {"name", (PyCFunction)Album_name, METH_NOARGS,
     "Returns the name of the album"
    },
    {"year", (PyCFunction)Album_year, METH_NOARGS,
     "Returns the year in which the album was released"
    },
    {"type", (PyCFunction)Album_type, METH_NOARGS,
     "Returns the type of the album, one of TYPE_ALBUM, TYPE_SINGLE," \
     "TYPE_COMPILATION or TYPE_UNKNOWN"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Album_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject AlbumType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Album",                          /*tp_name*/
    sizeof(Album),                            /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) Album_dealloc,               /*tp_dealloc*/
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
    (reprfunc) Album_str,                     /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Album objects",                          /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Album_methods,                            /* tp_methods */
    Album_members,                            /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Album_new,                                /* tp_new */
};

void
album_init(PyObject *module)
{
    if (PyType_Ready(&AlbumType) < 0)
        return;

    Py_INCREF(&AlbumType);
    PyModule_AddObject(module, "Album", (PyObject *)&AlbumType);

    /* Setup album type constants. */
    PyObject *album = Py_BuildValue("i", SP_ALBUMTYPE_ALBUM);
    PyObject *single = Py_BuildValue("i", SP_ALBUMTYPE_SINGLE);
    PyObject *compilation = Py_BuildValue("i", SP_ALBUMTYPE_COMPILATION);
    PyObject *unknown = Py_BuildValue("i", SP_ALBUMTYPE_UNKNOWN);

    PyMapping_SetItemString(AlbumType.tp_dict, "ALBUM", album);
    PyMapping_SetItemString(AlbumType.tp_dict, "SINGLE", single);
    PyMapping_SetItemString(AlbumType.tp_dict, "COMPILATION", compilation);
    PyMapping_SetItemString(AlbumType.tp_dict, "UNKNOWN", unknown);
}
