#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include "pyspotify.h"
#include "playlistfolder.h"

static PyMemberDef PlaylistFolder_members[] = {
    {NULL}
};

static PyObject *
PlaylistFolder_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    PlaylistFolder *self;

    self = (PlaylistFolder *) type->tp_alloc(type, 0);
    self->_name = "";
    self->_id = 0;
    self->_type = SP_PLAYLIST_TYPE_PLACEHOLDER;
    return (PyObject *)self;
}

PyObject *
PlaylistFolder_FromSpotify(sp_playlistcontainer *pc, int index, sp_playlist_type type)
{
    char *name;
    sp_error err;

    PyObject *pf =
        PyObject_CallObject((PyObject *)&PlaylistFolderType, NULL);
    ((PlaylistFolder *)pf)->_type = type;
    if (type == SP_PLAYLIST_TYPE_START_FOLDER) {
        ((PlaylistFolder *)pf)->_id =
            sp_playlistcontainer_playlist_folder_id(pc, index);
        name = PyMem_New(char, 256);
        err = sp_playlistcontainer_playlist_folder_name(pc, index, name, 256);
        ((PlaylistFolder *)pf)->_name = name;
        if (err > 0) {
            PyErr_SetString(SpotifyError, sp_error_message(err));
            return NULL;
        }
    }
    return pf;
}

static void
PlaylistFolder_dealloc(PlaylistFolder * self)
{
    if (self->_type == SP_PLAYLIST_TYPE_START_FOLDER)
        PyMem_Del(self->_name);
    self->ob_type->tp_free(self);
}


static PyObject *
PlaylistFolder_id(PlaylistFolder *self)
{
    return PyLong_FromLong(self->_id);
}

static PyObject *
PlaylistFolder_name(PlaylistFolder *self)
{
    return PyUnicode_FromString(self->_name);
}

static PyObject *
PlaylistFolder_type(PlaylistFolder *self)
{
    switch (self->_type) {
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
PlaylistFolder_is_loaded(PlaylistFolder *self)
{
    Py_INCREF(Py_True);
    return Py_True;
}

static PyMethodDef PlaylistFolder_methods[] = {
    {"id",
     (PyCFunction)PlaylistFolder_id,
     METH_NOARGS,
     "Returns this folder's id."},
    {"name",
     (PyCFunction)PlaylistFolder_name,
     METH_NOARGS,
     "Returns this folder's name."},
    {"type",
     (PyCFunction)PlaylistFolder_type,
     METH_NOARGS,
     "Returns this folder's type."},
    {"is_loaded",
     (PyCFunction)PlaylistFolder_is_loaded,
     METH_NOARGS,
     "Returns True."},
    {NULL}
};

PyTypeObject PlaylistFolderType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.PlaylistFolder",        /*tp_name */
    sizeof(PlaylistFolder),  /*tp_basicsize */
    0,                  /*tp_itemsize */
    (destructor) PlaylistFolder_dealloc,     /*tp_dealloc */
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
    0,                  /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "PlaylistFolder objects",        /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    PlaylistFolder_methods,  /* tp_methods */
    PlaylistFolder_members,  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    PlaylistFolder_new,      /* tp_new */
};

void
playlistfolder_init(PyObject *m)
{
    Py_INCREF(&PlaylistFolderType);
    PyModule_AddObject(m, "PlaylistFolder",
                       (PyObject *)&PlaylistFolderType);
}
