#include <Python.h>
#include <libspotify/api.h>
#include "pyspotify.h"

Callback *
create_trampoline(PyObject *callback, PyObject *userdata)
{
    /* TODO: switch to PyMem_Malloc and audit for coresponding free */
    Callback *trampoline = malloc(sizeof(Callback));

    if (userdata == NULL)
        userdata = Py_None;

    Py_INCREF(callback);
    Py_INCREF(userdata);
    trampoline->callback = callback;
    trampoline->userdata = userdata;
    return trampoline;
}

void
delete_trampoline(Callback * trampoline)
{
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    Py_DECREF(trampoline->userdata);
    Py_DECREF(trampoline->callback);
    free(trampoline);
    PyGILState_Release(gstate);
}

PyObject *
as_function(PyObject *o)
{
    if (PyMethod_Check(o)) {
        return PyMethod_GET_FUNCTION(o);
    }
    else {
        return o;
    }
}

PyObject *
error_message(sp_error error)
{
    if (error != SP_ERROR_OK)
        return PyUnicode_FromString(sp_error_message(error));
    Py_RETURN_NONE;
}

PyObject *
none_or_raise_error(sp_error error) {
    if (error == SP_ERROR_OK)
        Py_RETURN_NONE;
    PyErr_SetString(SpotifyError, sp_error_message(error));
    return NULL;
}
