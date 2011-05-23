/* $Id$
 *
 * Copyright 2011 Antoine Pierlot-Garcin
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

#include <Python.h>
#include <pyspotify.h>

Callback *create_trampoline(PyObject *callback, PyObject *manager,
                                                PyObject *userdata)
{
    Callback *tr = NULL;

    tr = malloc(sizeof(Callback));
    Py_INCREF(callback);
    Py_XINCREF(manager);
    Py_XINCREF(userdata);
    tr->callback = callback;
    tr->manager = manager;
    tr->userdata = userdata;
    return tr;
}

void delete_trampoline(Callback *tr)
{
    PyGILState_STATE gstate;

    gstate = PyGILState_Ensure();
    Py_XDECREF(tr->userdata);
    Py_XDECREF(tr->manager);
    Py_DECREF(tr->callback);
    free(tr);
    PyGILState_Release(gstate);
}

PyObject *as_function(PyObject *o)
{
    if (PyFunction_Check(o)) {
        return o;
    } else if (PyMethod_Check(o)) {
        return PyMethod_GET_FUNCTION(o);
    } else {
        PyErr_SetString(SpotifyError,
            "Expected function or method for a callback.");
        return NULL;
    }
}
