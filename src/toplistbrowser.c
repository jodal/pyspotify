#include <Python.h>
#include <structmember.h>
#include <libspotify/api.h>
#include <string.h>
#include "pyspotify.h"
#include "session.h"
#include "toplistbrowser.h"
#include "user.h"
#include "album.h"
#include "artist.h"
#include "track.h"

static PyMemberDef ToplistBrowser_members[] = {
    {NULL}
};


static void
ToplistBrowser_browse_complete(sp_toplistbrowse *toplistbrowse, void *userdata)
{
    Callback *tramp;
    PyObject *browser, *res;
    PyGILState_STATE gstate;

    if (!userdata)
        return;
    tramp = (Callback *)userdata;
    browser = ToplistBrowser_FromSpotify(toplistbrowse);
    gstate = PyGILState_Ensure();
    res = PyObject_CallFunctionObjArgs(tramp->callback, browser,
                                       tramp->userdata, NULL);
    if (!res)
        PyErr_WriteUnraisable(tramp->callback);
    delete_trampoline(tramp);
    Py_XDECREF(res);
    Py_DECREF(browser);
    PyGILState_Release(gstate);
}

static PyObject *
ToplistBrowser_new(PyTypeObject *potype, PyObject *args, PyObject *kwds)
{
    PyObject *self, *callback = NULL, *userdata = NULL, *region;
    sp_toplistbrowse *browser;
    sp_toplisttype tl_type = 0;
    sp_toplistregion tl_region = 0;
    char *type, *username = NULL;
    Callback *tramp = NULL;
    static char *kwlist[] =
        { "type", "region", "callback", "userdata", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "esO|OO", kwlist, ENCODING,
                                     &type, &region, &callback, &userdata))
        return NULL;
    if (callback) { // Optional callback
        if (!userdata)
            userdata = Py_None;
        tramp = create_trampoline(callback, NULL, userdata);
    }
    // Toplist type
    if (strcmp(type, "albums") == 0)
        tl_type = SP_TOPLIST_TYPE_ALBUMS;
    else if(strcmp(type, "artists") == 0)
        tl_type = SP_TOPLIST_TYPE_ARTISTS;
    else if (strcmp(type, "tracks") == 0)
        tl_type = SP_TOPLIST_TYPE_TRACKS;
    else {
        PyErr_Format(PyExc_ValueError,
                     "%s is not a valid toplist type", type);
        return NULL;
    }
    /* Region, can be
     *   - "XY" where XY is a 2 letter country code
     *   - "all" to get worlwide toplists
     *   - "current" to get the current user's toplists
     *   - user (spotify.User) to get this user's toplists
     */
    if (PyUnicode_Check(region)) {
            region = PyUnicode_AsUTF8String(region);
            if (!region)
                return NULL;
    } else
        Py_INCREF(region);
    if (PyBytes_Check(region)) {
            const char *reg = PyBytes_AS_STRING(region);
            if (strcmp(reg, "all") == 0)
                tl_region = SP_TOPLIST_REGION_EVERYWHERE;
            else if (strcmp(reg, "current") == 0)
                tl_region = SP_TOPLIST_REGION_USER;
            else
                tl_region = SP_TOPLIST_REGION(reg[0], reg[1]);
    } else if (region->ob_type == &UserType) {
        tl_region = SP_TOPLIST_REGION_USER;
        username = (char *) sp_user_canonical_name(((User *)region)->_user);
    }

    Py_BEGIN_ALLOW_THREADS
    browser = sp_toplistbrowse_create(g_session,
                                      tl_type, tl_region, username,
                                      (toplistbrowse_complete_cb *)
                                      ToplistBrowser_browse_complete,
                                      tramp);
    Py_END_ALLOW_THREADS

    Py_DECREF(region);
    self = potype->tp_alloc(potype, 0);
    ((ToplistBrowser *)self)->_toplistbrowse = browser;
    sp_toplistbrowse_add_ref(browser);
    return self;
}

PyObject *
ToplistBrowser_FromSpotify(sp_toplistbrowse * toplistbrowse)
{
    PyObject *tb = ToplistBrowserType.tp_alloc(&ToplistBrowserType, 0);

    ((ToplistBrowser *) tb)->_toplistbrowse = toplistbrowse;
    sp_toplistbrowse_add_ref(toplistbrowse);
    return tb;
}

static void
ToplistBrowser_dealloc(ToplistBrowser *self)
{
    if (self->_toplistbrowse)
        sp_toplistbrowse_release(self->_toplistbrowse);
    self->ob_type->tp_free(self);
}

static PyObject *
ToplistBrowser_is_loaded(ToplistBrowser *self)
{
    return PyBool_FromLong(sp_toplistbrowse_is_loaded(self->_toplistbrowse));
}

static PyObject *
ToplistBrowser_error(ToplistBrowser *self)
{
    return error_message(sp_toplistbrowse_error(self->_toplistbrowse));
}

/// Sequence protocol

Py_ssize_t
ToplistBrowser_sq_length(ToplistBrowser *self)
{
    int n;

    if ((n = sp_toplistbrowse_num_albums(self->_toplistbrowse)))
        return n;
    else if ((n = sp_toplistbrowse_num_artists(self->_toplistbrowse)))
        return n;
    else
        return sp_toplistbrowse_num_tracks(self->_toplistbrowse);
}

PyObject *
ToplistBrowser_sq_item(ToplistBrowser *self, Py_ssize_t index)
{
    if (index < sp_toplistbrowse_num_albums(self->_toplistbrowse)) {
        return Album_FromSpotify(
                sp_toplistbrowse_album(self->_toplistbrowse, (int)index));
    }
    else if (index < sp_toplistbrowse_num_artists(self->_toplistbrowse)) {
        return Artist_FromSpotify(
                sp_toplistbrowse_artist(self->_toplistbrowse, (int)index));
    }
    else if (index < sp_toplistbrowse_num_tracks(self->_toplistbrowse)) {
        return Track_FromSpotify(
                sp_toplistbrowse_track(self->_toplistbrowse, (int)index));
    }
    else {
        PyErr_SetString(PyExc_IndexError, "");
        return NULL;
    }
}

PySequenceMethods ToplistBrowser_as_sequence = {
    (lenfunc) ToplistBrowser_sq_length,   // sq_length
    0,                  // sq_concat
    0,                  // sq_repeat
    (ssizeargfunc) ToplistBrowser_sq_item,        // sq_item
    0,                  // sq_ass_item
    0,                  // sq_contains
    0,                  // sq_inplace_concat
    0,                  // sq_inplace_repeat
};

static PyMethodDef ToplistBrowser_methods[] = {
    {"is_loaded",
     (PyCFunction) ToplistBrowser_is_loaded,
     METH_NOARGS,
     "True if this toplist browser has been loaded by the client"},
    {"error",
     (PyCFunction) ToplistBrowser_error,
     METH_NOARGS,
     ""},
    {NULL}
};

PyTypeObject ToplistBrowserType = {
    PyObject_HEAD_INIT(NULL)
    0,                  /*ob_size */
    "spotify.ToplistBrowser",     /*tp_name */
    sizeof(ToplistBrowser),       /*tp_basicsize */
    0,                  /*tp_itemsize */
    (destructor) ToplistBrowser_dealloc,        /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    0,                  /*tp_repr */
    0,                  /*tp_as_number */
    &ToplistBrowser_as_sequence,     /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    0,                  /*tp_call */
    0,                  /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    0,                  /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags */
    "ToplistBrowser objects",   /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    ToplistBrowser_methods,     /* tp_methods */
    ToplistBrowser_members,     /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    0,                  /* tp_init */
    0,                  /* tp_alloc */
    ToplistBrowser_new,         /* tp_new */
};

void
toplistbrowser_init(PyObject *m)
{
    Py_INCREF(&ToplistBrowserType);
    PyModule_AddObject(m, "ToplistBrowser", (PyObject *)&ToplistBrowserType);
}
