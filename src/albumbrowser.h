#include "pyspotify.h"

typedef struct {
    PyObject_HEAD sp_albumbrowse *_browser;
    Callback _callback;
} AlbumBrowser;

extern PyTypeObject AlbumBrowserType;

extern void albumbrowser_init(PyObject *m);

PyObject *
AlbumBrowser_FromSpotify(sp_albumbrowse *browse);
