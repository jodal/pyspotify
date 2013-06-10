#include "pyspotify.h"

typedef struct {
    PyObject_HEAD
    sp_albumbrowse *_browser;
} AlbumBrowser;

#define AlbumBrowser_SP_ALBUMBROWSE(a) ((AlbumBrowser *)a)->_browser

extern PyTypeObject AlbumBrowserType;

PyObject  *
AlbumBrowser_FromSpotify(sp_albumbrowse *browser);

void
albumbrowser_init(PyObject *module);
