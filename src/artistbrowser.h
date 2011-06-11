#include "pyspotify.h"

typedef struct {
    PyObject_HEAD sp_artistbrowse *_browser;
    Callback _callback;
} ArtistBrowser;

extern PyTypeObject ArtistBrowserType;

extern void artistbrowser_init(PyObject *m);
