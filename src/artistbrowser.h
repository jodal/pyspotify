#include "pyspotify.h"

typedef struct {
    PyObject_HEAD
    sp_artistbrowse *_browser;
} ArtistBrowser;

extern PyTypeObject ArtistBrowserType;

extern void artistbrowser_init(PyObject *m);

PyObject *
ArtistBrowser_FromSpotify(sp_artistbrowse * browse);
