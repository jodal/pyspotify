#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "track.h"
#include "artist.h"
#include "album.h"
#include "session.h"

static PyObject *
Track_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *self = type->tp_alloc(type, 0);
    Track_SP_TRACK(self) = NULL;
    return self;
}

PyObject *
Track_FromSpotify(sp_track *track, bool add_ref)
{
    PyObject *self = TrackType.tp_alloc(&TrackType, 0);
    Track_SP_TRACK(self) = track;
    if (add_ref)
        sp_track_add_ref(track);
    return self;
}

static void
Track_dealloc(PyObject *self)
{
    if (Track_SP_TRACK(self) != NULL)
        sp_track_release(Track_SP_TRACK(self));
    self->ob_type->tp_free(self);
}

static PyObject *
Track_is_loaded(PyObject *self)
{
    return PyBool_FromLong(sp_track_is_loaded(Track_SP_TRACK(self)));
}

static PyObject *
Track_artists(PyObject *self, PyObject *args)
{
    sp_artist *artist;
    int i;
    int count = sp_track_num_artists(Track_SP_TRACK(self));
    PyObject *list = PyList_New(count);

    for (i = 0; i < count; ++i) {
        artist = sp_track_artist(Track_SP_TRACK(self), i);
        PyList_SET_ITEM(list, i, Artist_FromSpotify(artist, 1 /* add_ref */));
    }
    return list;
}

static PyObject *
Track_album(PyObject *self)
{
    sp_album *album = sp_track_album(Track_SP_TRACK(self));
    if (album == NULL)
        Py_RETURN_NONE;
    return Album_FromSpotify(album, 1 /* add_ref */);
}

static PyObject *
Track_name(PyObject *self)
{
    const char *name = sp_track_name(Track_SP_TRACK(self));
    return PyUnicode_FromString(name);
}

static PyObject *
Track_str(PyObject *self)
{
    return Track_name(self);
}

static PyObject *
Track_duration(PyObject *self)
{
    return Py_BuildValue("i", sp_track_duration(Track_SP_TRACK(self)));
}

static PyObject *
Track_popularity(PyObject *self)
{
    return Py_BuildValue("i", sp_track_popularity(Track_SP_TRACK(self)));
}

static PyObject *
Track_disc(PyObject *self)
{
    return Py_BuildValue("i", sp_track_disc(Track_SP_TRACK(self)));
}

static PyObject *
Track_index(PyObject *self)
{
    return Py_BuildValue("i", sp_track_index(Track_SP_TRACK(self)));
}

static PyObject *
Track_error(PyObject *self)
{
    /* TODO: return enums that represent sp_error */
    sp_error error = sp_track_error(Track_SP_TRACK(self));
    return Py_BuildValue("i", error);
}

static PyObject *
Track_starred(PyObject *self, PyObject *args, PyObject *kwds)
{
    /* TODO: this could just be using g_session */
    PyObject *session, *starred = NULL;
    static char *kwlist[] = { "session", "set", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O!", kwlist, &SessionType,
                                     &session, &PyBool_Type, &starred))
        return NULL;

    if (starred != NULL)  /* Cast is to convert single track to "array" */
        sp_track_set_starred(Session_SP_SESSION(session),
                             (sp_track * const*)&(Track_SP_TRACK(self)),
                             1, starred == Py_True);

    return PyBool_FromLong(sp_track_is_starred(
        Session_SP_SESSION(session), Track_SP_TRACK(self)));
}

static PyObject *
Track_availability(PyObject *self)
{
    /* TODO: return enums that represent sp_availability */
    enum sp_availability availability = sp_track_get_availability(
        g_session, Track_SP_TRACK(self));
    return Py_BuildValue("i", availability);
}

static PyObject *
Track_is_local(PyObject *self)
{
    return PyBool_FromLong(sp_track_is_local(g_session, Track_SP_TRACK(self)));
}

static PyObject *
Track_is_autolinked(PyObject *self)
{
    return PyBool_FromLong(sp_track_is_autolinked(
        g_session, Track_SP_TRACK(self)));
}

static PyObject *
Track_get_playable(PyObject *self)
{
    return Track_FromSpotify(sp_track_get_playable(
        g_session, Track_SP_TRACK(self)), 1 /* add_ref */);
}

static PyMethodDef Track_methods[] = {
    {"availability", (PyCFunction)Track_availability, METH_NOARGS,
     "Get availability status for this track."
    },
    {"is_loaded", (PyCFunction)Track_is_loaded, METH_NOARGS,
     "Get load status for this track. If the track is not loaded yet, all " \
     "other functions operating on the track return default values."
    },
    {"is_local",
     (PyCFunction)Track_is_local, METH_NOARGS,
     "Returns whether this track is local, ie. created with the API."
    },
    {"artists", (PyCFunction)Track_artists, METH_VARARGS,
     "The artists who performed this track."
    },
    {"album", (PyCFunction)Track_album, METH_NOARGS,
     "The album of this track."
    },
    {"name", (PyCFunction)Track_name, METH_NOARGS,
     "The name of this track"
    },
    {"duration", (PyCFunction)Track_duration, METH_NOARGS,
     "The duration of this track"
    },
    {"popularity", (PyCFunction)Track_popularity, METH_NOARGS,
     "The popularity of this track"
    },
    {"disc", (PyCFunction)Track_disc, METH_NOARGS,
     "The disc number of this track"
    },
    {"index", (PyCFunction)Track_index, METH_NOARGS,
     "The position of this track on its disc"
    },
    {"error", (PyCFunction)Track_error, METH_NOARGS,
     "The error associated with this track"
    },
    {"starred", (PyCFunction)Track_starred, METH_VARARGS | METH_KEYWORDS,
     "Get/set the starred property of the track"
    },
    {"is_autolinked", (PyCFunction)Track_is_autolinked, METH_NOARGS,
     "Returns whether this track is a link to another track"
    },
    {"playable", (PyCFunction)Track_get_playable, METH_NOARGS,
     "Return the actual track that will be played if this track is played"
    },
    {NULL} /* Sentinel */
};

static PyMemberDef Track_members[] = {
    {NULL} /* Sentinel */
};

PyTypeObject TrackType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /*ob_size*/
    "spotify.Track",                          /*tp_name*/
    sizeof(Track),                            /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor) Track_dealloc,               /*tp_dealloc*/
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
    Track_str,                                /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Track objects",                          /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    Track_methods,                            /* tp_methods */
    Track_members,                            /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    Track_new,                                /* tp_new */
};

void
track_init(PyObject *module)
{
    if (PyType_Ready(&TrackType) < 0)
        return;

    Py_INCREF(&TrackType);
    PyModule_AddObject(module, "Track", (PyObject *)&TrackType);
}
