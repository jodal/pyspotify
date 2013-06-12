#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include "pyspotify.h"
#include "playlistfolder.h"

/* TODO: store type, container and index instead? */
static PyObject *
PlaylistFolder_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    PlaylistFolder_NAME(self) = "";
    PlaylistFolder_ID(self) = 0;
    PlaylistFolder_SP_PLAYLIST_TYPE(self) = SP_PLAYLIST_TYPE_PLACEHOLDER;
    return self;
}

/* NOTE: this is the only *_FromSpotify that does not ref count anything... */
PyObject *
PlaylistFolder_FromSpotify(sp_playlistcontainer *container, int index,
                           sp_playlist_type type)
{
    sp_error error;

    /* TODO: consider using callobject in this and other FromSpotify calls? */
    PyObject *self = PlaylistFolderType.tp_alloc(&PlaylistFolderType, 0);
    PlaylistFolder_NAME(self) = "";
    PlaylistFolder_ID(self) = 0;
    PlaylistFolder_SP_PLAYLIST_TYPE(self) = type;

    if (type == SP_PLAYLIST_TYPE_START_FOLDER) {
        PlaylistFolder_ID(self) = sp_playlistcontainer_playlist_folder_id(
            container, index);

        PlaylistFolder_NAME(self) = PyMem_New(char, 256);
        error = sp_playlistcontainer_playlist_folder_name(
            container, index, PlaylistFolder_NAME(self), 256);

        if (error != SP_ERROR_OK) {
            PyErr_SetString(SpotifyError, sp_error_message(error));
            return NULL;
        }
    }
    return self;
}

static void
PlaylistFolder_dealloc(PyObject *self)
{
    if (PlaylistFolder_SP_PLAYLIST_TYPE(self) == SP_PLAYLIST_TYPE_START_FOLDER)
        PyMem_Del(PlaylistFolder_NAME(self));
    self->ob_type->tp_free(self);
}


static PyObject *
PlaylistFolder_id(PyObject *self)
{
    return PyLong_FromUnsignedLongLong(PlaylistFolder_ID(self));
}

static PyObject *
PlaylistFolder_name(PyObject *self)
{
    return PyUnicode_FromString((PlaylistFolder_NAME(self)));
}

static PyObject *
PlaylistFolder_type(PyObject *self)
{
    switch (PlaylistFolder_SP_PLAYLIST_TYPE(self)) {
    case SP_PLAYLIST_TYPE_START_FOLDER:
        return PyBytes_FromString("folder_start");
        break;

    case SP_PLAYLIST_TYPE_END_FOLDER:
        return PyBytes_FromString("folder_end");
        break;

    case SP_PLAYLIST_TYPE_PLACEHOLDER:
    default:
        return PyBytes_FromString("placeholder");
        break;
    }
}

static PyObject *
PlaylistFolder_is_loaded(PyObject *self)
{
    Py_INCREF(Py_True);
    return Py_True;
}

static PyMethodDef PlaylistFolder_methods[] = {
    {"id", (PyCFunction)PlaylistFolder_id, METH_NOARGS,
     "Returns this folder's id."
    },
    {"name", (PyCFunction)PlaylistFolder_name, METH_NOARGS,
     "Returns this folder's name."
    },
    {"type", (PyCFunction)PlaylistFolder_type, METH_NOARGS,
     "Returns this folder's type."
    },
    {"is_loaded", (PyCFunction)PlaylistFolder_is_loaded, METH_NOARGS,
     "Returns True."
    },
    {NULL} /* Sentinel */
};

static PyMemberDef PlaylistFolder_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject PlaylistFolderType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.PlaylistFolder",                 /*tp_name*/
    sizeof(PlaylistFolder),                   /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) PlaylistFolder_dealloc,      /*tp_dealloc*/
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
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "PlaylistFolder objects",                 /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    PlaylistFolder_methods,                   /* tp_methods */
    PlaylistFolder_members,                   /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    PlaylistFolder_new,                       /* tp_new */
};

void
playlistfolder_init(PyObject *module)
{
    Py_INCREF(&PlaylistFolderType);
    PyModule_AddObject(module, "PlaylistFolder",
                       (PyObject *)&PlaylistFolderType);
}
