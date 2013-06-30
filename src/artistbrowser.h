#include "pyspotify.h"

typedef struct {
    PyObject_HEAD
    sp_artistbrowse *_browser;
} ArtistBrowser;

#define ArtistBrowser_SP_ARTISTBROWSE(o) ((ArtistBrowser *)o)->_browser

extern PyTypeObject ArtistBrowserType;

PyObject *
ArtistBrowser_FromSpotify(sp_artistbrowse *browser, bool add_ref);

extern void
artistbrowser_init(PyObject *module);
