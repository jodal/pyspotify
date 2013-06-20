#pragma once

/* See http://stackoverflow.com/a/1644898 for details of the hows and whys:
 * Note that ##__VA_ARGS__ is gcc-ism, we might need to create a debug_print
 * macro for the cases where there are no arguments to the printf.
 */
#ifndef DEBUG
#define DEBUG 0
#endif
#define debug_printf(fmt, ...) \
        do { if (DEBUG) fprintf(stderr, "[pyspotify] %s:%d:%s(): " fmt "\n", \
                __FILE__, __LINE__, __func__, ##__VA_ARGS__); } while (0)

#include <Python.h>

#define ENCODING "utf-8"

/* TODO: remove this? */
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
    PyObject *userdata;
} Callback;

/* Trampolines for callback handling */
Callback *create_trampoline(PyObject *callback, PyObject *userdata);
void delete_trampoline(Callback *trampoline);

/* Returns o as a function ; o must be a method or a function object
 *   o is a Function object: returns o
 *   o is a Method object  : returns the corresponding function
 */
PyObject *as_function(PyObject *o);

/* Returns a Python string for the error, or None if SP_ERROR_OK */
PyObject *error_message(sp_error error);
PyObject *none_or_raise_error(sp_error error);
