#pragma once

// define DEBUG to get lots of extra crap printed out
// #define DEBUG 1

#include <Python.h>

#define ENCODING "utf-8"

#if (PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION < 6)
#define PyBytes_AS_STRING            PyString_AS_STRING
#define PyBytes_AsStringAndSize      PyString_AsStringAndSize
#define PyBytes_Check                PyString_Check
#define PyBytes_FromString           PyString_FromString
#define PyBytes_FromStringAndSize    PyString_FromStringAndSize
#define PyUnicode_FromString         PyString_FromString
#endif

extern PyObject *SpotifyError;
extern PyObject *SpotifyApiVersion;

typedef struct {
    PyObject *callback;
    PyObject *manager;
    PyObject *userdata;
} Callback;

/* Trampolines for callback handling */
Callback *create_trampoline(PyObject *callback, PyObject *manager,
                            PyObject *userdata);
void delete_trampoline(Callback * tr);

/* Returns o as a function ; o must be a method or a function object
 *   o is a Function object: returns o
 *   o is a Method object  : returns the corresponding function
 */
PyObject *as_function(PyObject *o);

/* Returns a Python string for the error, or None if SP_ERROR_OK */
PyObject *error_message(int err);
