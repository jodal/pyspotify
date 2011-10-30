#include <Python.h>
#include <structmember.h>
#include "libspotify/api.h"
#include "pyspotify.h"
#include "track.h"
#include "artist.h"
#include "album.h"
#include "session.h"

static PyMemberDef Track_members[] = {
    {NULL}
};

static PyObject *
Track_new(PyTypeObject * type, PyObject *args, PyObject *kwds)
{
    Track *self;

    self = (Track *) type->tp_alloc(type, 0);
    self->_track = NULL;
    return (PyObject *)self;
}

PyObject *
Track_FromSpotify(sp_track * track)
{
    PyObject *t = PyObject_CallObject((PyObject *)&TrackType, NULL);

    ((Track *) t)->_track = track;
    sp_track_add_ref(track);
    return t;
}

static void
Track_dealloc(Track * self)
{
    if (self->_track)
        sp_track_release(self->_track);
    self->ob_type->tp_free(self);
}

static PyObject *
Track_str(PyObject *oself)
{
    Track *self = (Track *) oself;
    const char *s = sp_track_name(self->_track);

    return PyUnicode_FromString(s);
}

static PyObject *
Track_is_loaded(Track * self)
{
    return Py_BuildValue("i", sp_track_is_loaded(self->_track));
}

static PyObject *
Track_artists(Track * self, PyObject *args)
{
    sp_artist *artist;
    int count = sp_track_num_artists(self->_track);
    PyObject *l = PyList_New(count);
    int i;

    for (i = 0; i < count; i++) {
        artist = sp_track_artist(self->_track, i);
        PyObject *a = Artist_FromSpotify(artist);

        PyList_SetItem(l, i, a);
    }
    return l;
}

static PyObject *
Track_album(Track * self)
{
    sp_album *album;

    album = sp_track_album(self->_track);
    if (!album)
        Py_RETURN_NONE;
    PyObject *a = Album_FromSpotify(album);

    return a;
}

static PyObject *
Track_name(Track * self)
{
    const char *s = sp_track_name(self->_track);

    return PyUnicode_FromString(s);
}

static PyObject *
Track_duration(Track * self)
{
    return Py_BuildValue("i", sp_track_duration(self->_track));
}

static PyObject *
Track_popularity(Track * self)
{
    return Py_BuildValue("i", sp_track_popularity(self->_track));
}

static PyObject *
Track_disc(Track * self)
{
    return Py_BuildValue("i", sp_track_disc(self->_track));
}

static PyObject *
Track_index(Track * self)
{
    return Py_BuildValue("i", sp_track_index(self->_track));
}

static PyObject *
Track_error(Track * self)
{
    return Py_BuildValue("i", sp_track_error(self->_track));
}

static PyObject *
Track_starred(Track * self, PyObject *args, PyObject *kwds)
{
    int set;
    PyObject *bset = NULL;
    Session *session;
    static char *kwlist[] = { "session", "set", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O!", kwlist,
                                     &SessionType, &session, &PyBool_Type,
                                     &bset))
        return NULL;
    if (bset) {
        set = (bset == Py_True);
        sp_track_set_starred(session->_session,
                             (sp_track * const*)&(self->_track), 1, set);
    }
    return (PyObject *)PyBool_FromLong((long)
                                       sp_track_is_starred(session->_session,
                                                           self->_track));
}

static PyObject *
Track_availability(Track *self)
{
    return Py_BuildValue("i",
                         sp_track_get_availability(g_session, self->_track));
}

static PyObject *
Track_is_local(Track *self)
{
    return PyBool_FromLong(sp_track_is_local(g_session, self->_track));
}

static PyMethodDef Track_methods[] = {
    {"availability",
     (PyCFunction)Track_availability,
     METH_NOARGS,
     "Get availability status for this track."},
    {"is_loaded",
     (PyCFunction)Track_is_loaded,
     METH_NOARGS,
     "Get load status for this track. If the track is not loaded yet, all other functions operating on the track return default values."},
    {"is_local",
     (PyCFunction)Track_is_local,
     METH_NOARGS,
     "Returns wether this track is local, ie. created with the API."},
    {"artists",
     (PyCFunction)Track_artists,
     METH_VARARGS,
     "The artists who performed this track."},
    {"album",
     (PyCFunction)Track_album,
     METH_NOARGS,
     "The album of this track."},
    {"name",
     (PyCFunction)Track_name,
     METH_NOARGS,
     "The name of this track"},
    {"duration",
     (PyCFunction)Track_duration,
     METH_NOARGS,
     "The duration of this track"},
    {"popularity",
     (PyCFunction)Track_popularity,
     METH_NOARGS,
     "The popularity of this track"},
    {"disc",
     (PyCFunction)Track_disc,
     METH_NOARGS,
     "The disc number of this track"},
    {"index",
     (PyCFunction)Track_index,
     METH_NOARGS,
     "The position of this track on its disc"},
    {"error",
     (PyCFunction)Track_error,
     METH_NOARGS,
     "The error associated with this track"},
    {"starred",
     (PyCFunction)Track_starred,
     METH_VARARGS | METH_KEYWORDS,
     "Get/set the starred property of the track"},
    {NULL}
};

PyTypeObject TrackType = {
    PyObject_HEAD_INIT(NULL) 0, /*ob_size */
    "spotify.Track",    /*tp_name */
    sizeof(Track),      /*tp_basicsize */
    0,                  /*tp_itemsize */
    (destructor) Track_dealloc, /*tp_dealloc */
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
    Track_str,          /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "Track objects",    /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    Track_methods,      /* tp_methods */
    Track_members,      /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    Track_new,          /* tp_new */
};

void
track_init(PyObject *m)
{
    Py_INCREF(&TrackType);
    PyModule_AddObject(m, "Track", (PyObject *)&TrackType);
}
